import numpy as np
from numba import jit, prange
from numba import types
from numba.typed import List
from .math3d import rotation_matrices
from .setting import AMBIENT, INTENSITY

@jit(nopython=True, fastmath=True, parallel=True)
def create_diffuse_buffer_parallel(mesh_list, pivot_list, pos_list, rot_list, light_pos_list, diffuse_list, temp):
    n_meshes = len(mesh_list)
    n_lights = len(light_pos_list) 
    diffuse_list.clear()
    
    ONE_THIRD = np.float32(0.333333)
    EPSILON = np.float32(1e-9)
    ZERO = np.float32(0.0)
    ONE = np.float32(1.0)
    UP_VECTOR = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    VAL_AMBIENT = np.float32(AMBIENT)
    VAL_INTENSITY = np.float32(INTENSITY)

    for m_id in prange(n_meshes):
        idx = np.int64(m_id)
        mesh = mesh_list[idx]
        n_tris = mesh.shape[0]
        
        if n_tris == 0: continue
            
        pivot = pivot_list[idx]
        pos = pos_list[idx]
        rot = rot_list[idx]
        
        rx_m, ry_m, rz_m = rotation_matrices(rot[0], rot[1], rot[2])
        rot_mat = rz_m @ ry_m @ rx_m
        rot_3x3 = np.ascontiguousarray(rot_mat[:3, :3].T).astype(np.float32)

        for i in range(n_tris):
            tri_w = (mesh[i] - pivot) @ rot_3x3 + pivot + pos
            v0, v1, v2 = tri_w[0], tri_w[1], tri_w[2]
            
            center = (v0 + v1 + v2) * ONE_THIRD
            
            normal = np.cross(v1 - v0, v2 - v0)
            n_len = np.float32(np.linalg.norm(normal))
            
            if n_len > EPSILON:
                normal /= n_len
            else:
                normal[:] = UP_VECTOR
            
            diffuse_sum = ZERO
            
            for l_idx in range(n_lights):
                l_pos = light_pos_list[l_idx]
                to_light = l_pos - center
                dist = np.float32(np.linalg.norm(to_light)) + EPSILON
                
                dot = np.dot(normal, to_light / dist)
                
                if dot > ZERO:
                    diffuse_sum += dot
            
            val = VAL_AMBIENT + diffuse_sum * VAL_INTENSITY
            temp[m_id, i] = min(val, ONE)

    for m_id in range(n_meshes):
        diffuse_list.append(temp[m_id])

@jit(nopython=True, fastmath=True, parallel=True)
def create_diffuse_buffer_serial(mesh_list, pivot_list, pos_list, rot_list, light_pos_list, diffuse_list, temp):
    n_meshes = len(mesh_list)
    n_lights = len(light_pos_list) 
    diffuse_list.clear()
    
    ONE_THIRD = np.float32(0.333333)
    EPSILON = np.float32(1e-9)
    ZERO = np.float32(0.0)
    ONE = np.float32(1.0)
    UP_VECTOR = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    VAL_AMBIENT = np.float32(AMBIENT)
    VAL_INTENSITY = np.float32(INTENSITY)

    for m_id in range(n_meshes):
        idx = np.int64(m_id)
        mesh = mesh_list[idx]
        n_tris = mesh.shape[0]
        
        if n_tris == 0: continue
            
        pivot = pivot_list[idx]
        pos = pos_list[idx]
        rot = rot_list[idx]
        
        rx_m, ry_m, rz_m = rotation_matrices(rot[0], rot[1], rot[2])
        rot_mat = rz_m @ ry_m @ rx_m
        rot_3x3 = np.ascontiguousarray(rot_mat[:3, :3].T).astype(np.float32)

        for i in range(n_tris):
            tri_w = (mesh[i] - pivot) @ rot_3x3 + pivot + pos
            v0, v1, v2 = tri_w[0], tri_w[1], tri_w[2]
            
            center = (v0 + v1 + v2) * ONE_THIRD
            
            normal = np.cross(v1 - v0, v2 - v0)
            n_len = np.float32(np.linalg.norm(normal))
            
            if n_len > EPSILON:
                normal /= n_len
            else:
                normal[:] = UP_VECTOR
            
            diffuse_sum = ZERO
            
            for l_idx in range(n_lights):
                l_pos = light_pos_list[l_idx]
                to_light = l_pos - center
                dist = np.float32(np.linalg.norm(to_light)) + EPSILON
                
                dot = np.dot(normal, to_light / dist)
                
                if dot > ZERO:
                    diffuse_sum += dot
            
            val = VAL_AMBIENT + diffuse_sum * VAL_INTENSITY
            temp[m_id, i] = min(val, ONE)

    for m_id in range(n_meshes):
        diffuse_list.append(temp[m_id])

def create_diffuse_buffer(mesh_list, pivot_list, pos_list, rot_list, light_pos_list, diffuse_list, temp, mode):
    if mode:
        create_diffuse_buffer_parallel(mesh_list, pivot_list, pos_list, rot_list, light_pos_list, diffuse_list, temp)
    else:
        create_diffuse_buffer_serial(mesh_list, pivot_list, pos_list, rot_list, light_pos_list, diffuse_list, temp)