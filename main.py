import sdl2
import numpy as np
import time
import traceback

from renderer import Renderer
from compiler import compile_renderer
from loader.mesh_loader import load_scene, load_mesh

def main():
    print("=" * 60)
    print("🧪 Starting Renderer Test Program")
    print("=" * 60)
    
    if not compile_renderer():
        print("❌ Compilation failed! Exiting...")
        return
    print("✅ Compilation successful!\n")
    
    try:
        renderer = Renderer(width=800, height=600, title="Renderer Test")
        print("✅ Renderer initialized!\n")
    except Exception as e:
        print(f"❌ Failed to initialize renderer: {e}")
        traceback.print_exc()
        return
    
    try:
        meshes, texs, uvs, nodes, bounds, pos_list, rot_list = load_scene("res/chess_pieces.glb", True)
        for i in range(len(meshes)):
            renderer.add_mesh(
                position=pos_list[i],
                pivot=(0, 0, 0),
                rotation=rot_list[i],
                loaded_meshes=meshes[i],
                loaded_texs=texs[i],
                loaded_uvs=uvs[i],
                aabb_data=bounds[i]
            )

        total_polygons = 0
        for mesh in meshes:
            total_polygons += len(mesh) 
        
        print(f"📊 Mesh info: {len(meshes)} meshes, {total_polygons} triangles")
        
        if total_polygons > 20000:
            print(f"🚨 CRITICAL: Very high poly count ({total_polygons} tris).")
        elif total_polygons > 10000:
            print(f"⚠️  WARNING: High poly count ({total_polygons} tris).")

        print()

    except Exception as e:
        print(f"❌ Failed to load scene: {e}")
        traceback.print_exc()
        renderer.cleanup()
        return
    
    try:
        light1 = renderer.add_light((0.0, 10.0, 0.0), (0.0, 0.0, 0.0))
        print(f"✅ Lights added! IDs: {light1}\n")
    except Exception as e:
        print(f"❌ Failed to add lights: {e}")
        traceback.print_exc()
        renderer.cleanup()
        return
    
    renderer.set_camera_position((0.0, 10.0, -8.0))
    renderer.set_camera_target((0.0, 0.0, 0.0))
    yaw = 0.0
    pitch = 0.0
    print("✅ Camera configured!\n")
    
    print("=" * 60)
    print("🎮 Starting main loop")
    print("=" * 60)
    print("\n📝 Controls:")
    print("  W/S/A/D    - Move camera")
    print("  SPACE      - Move up")
    print("  CTRL       - Move down")
    print("  Mouse      - Look around")
    print("  E/Q/Click  - Choose Object")
    print("  Arrow      - Move Object")
    print("  TAB        - Reset camera to look at origin")
    print("  ESC        - Release mouse")
    print("  Close window to exit")
    print()
    
    running = True
    event = sdl2.SDL_Event()
    
    mouse_sensitivity = 0.0015
    move_speed = 1
    fps_record = []
    
    sdl2.SDL_SetRelativeMouseMode(True)
    renderer.show()
    
    frame_count = 0
    start_time = time.perf_counter()
    idx = 0
    
    try:
        while running:
            while sdl2.SDL_PollEvent(event):
                if event.type == sdl2.SDL_QUIT:
                    running = False
                    print("\n👋 Quit signal received")
                
                elif event.type == sdl2.SDL_WINDOWEVENT:
                    if event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_GAINED:
                        sdl2.SDL_SetRelativeMouseMode(True)
                    elif event.window.event == sdl2.SDL_WINDOWEVENT_FOCUS_LOST:
                        sdl2.SDL_SetRelativeMouseMode(False)
                
                elif event.type == sdl2.SDL_KEYDOWN:
                    key = event.key.keysym.sym
                    if key == sdl2.SDLK_ESCAPE:
                        sdl2.SDL_SetRelativeMouseMode(False)
                    elif key == sdl2.SDLK_TAB:
                        renderer.set_camera_target(0.0, 0.0, 0.0)
                        print("🎯 Camera reset to look at origin")
                    elif key == sdl2.SDLK_q:
                        idx -= 1
                        if idx < 0: idx = len(meshes) - 1
                        box = bounds[idx]
                        width = box[1][0] - box[0][0]   
                        height = box[1][1] - box[0][1]  
                        depth = box[1][2] - box[0][2]   
                        print(f"- Box {idx} size: {width:.2f} x {height:.2f} x {depth:.2f}")
                    
                    elif key == sdl2.SDLK_e:
                        idx += 1
                        if idx >= len(meshes): idx = 0
                        box = bounds[idx]
                        width = box[1][0] - box[0][0]   
                        height = box[1][1] - box[0][1]  
                        depth = box[1][2] - box[0][2]   
                        print(f"- Box {idx} size: {width:.2f} x {height:.2f} x {depth:.2f}")

                elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                    if event.button.button == sdl2.SDL_BUTTON_LEFT:
                        x = event.button.x
                        y = event.button.y
                        idx = renderer.object_buffer[y, x]
                    else: sdl2.SDL_SetRelativeMouseMode(True)
                
                elif event.type == sdl2.SDL_MOUSEMOTION and sdl2.SDL_GetRelativeMouseMode():
                    dx, dy = event.motion.xrel, event.motion.yrel
                    yaw += dx * mouse_sensitivity
                    pitch += dy * mouse_sensitivity
                    renderer.rotate_camera(yaw, pitch)
            
            keystate = sdl2.SDL_GetKeyboardState(None)
            if keystate[sdl2.SDL_SCANCODE_W]:
                renderer.move_camera(forward=move_speed)
            if keystate[sdl2.SDL_SCANCODE_S]:
                renderer.move_camera(forward=-move_speed)
            if keystate[sdl2.SDL_SCANCODE_A]:
                renderer.move_camera(right=-move_speed)
            if keystate[sdl2.SDL_SCANCODE_D]:
                renderer.move_camera(right=move_speed)
            if keystate[sdl2.SDL_SCANCODE_SPACE]:
                renderer.move_camera(up=move_speed)
            if keystate[sdl2.SDL_SCANCODE_LCTRL]:
                renderer.move_camera(up=-move_speed)

            pos = renderer.pos_list[idx]
            if keystate[sdl2.SDL_SCANCODE_UP]: pos[0] += move_speed
            if keystate[sdl2.SDL_SCANCODE_DOWN]: pos[0] -= move_speed
            if keystate[sdl2.SDL_SCANCODE_LEFT]: pos[2] -= move_speed
            if keystate[sdl2.SDL_SCANCODE_RIGHT]: pos[2] += move_speed
            
            renderer.set_mesh_transform(idx, position=pos)

            renderer.update_light()

            renderer.render_meshes()
            renderer.render_lights()
            renderer.render_bounding_box(idx, 1, (255, 0, 0, 255))
            renderer.present()
            renderer.update_fps_display()
            
            frame_count += 1
            
            if frame_count % 100 == 0:
                elapsed = time.perf_counter() - start_time
                stats = renderer.get_stats()
                fps_record.append(stats['fps'])
    
    except KeyboardInterrupt:
        print("\n⚠️  Keyboard interrupt received")
    except Exception as e:
        print(f"\n❌ Error in main loop: {e}")
        traceback.print_exc()
    finally:
        print("\n📋 Cleaning up...")
        renderer.cleanup()
        
        elapsed = time.perf_counter() - start_time
        if frame_count > 0:
            if len(fps_record) != 0: avg_fps = sum(fps_record)/len(fps_record)
            else: avg_fps = frame_count / elapsed
            print("\n" + "=" * 60)
            print("📊 Final Statistics")
            print("=" * 60)
            print(f"  Total frames:     {frame_count}")
            print(f"  Total time:       {elapsed:.2f}s")
            print(f"  Average FPS:      {avg_fps:.2f}")
            print(f"  Rendering mode:   {'CPU (Parallel)' if renderer.parallel else 'CPU (Serial)'}")
            print("=" * 60)
        
        print("\n✅ Test program finished successfully!")


if __name__ == "__main__":
    main()