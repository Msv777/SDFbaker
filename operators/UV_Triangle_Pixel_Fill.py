import bpy # type: ignore
import bmesh # type: ignore
from mathutils import Vector # type: ignore
import numpy as np
import math



# 判断点是否在三角形内部的函数
def is_point_inside_triangle(point, uv_coords):
    # 提取顶点坐标和UV坐标
    v1, v2, v3 = uv_coords
    x1, y1 = v1[0], v1[1]
    x2, y2 = v2[0], v2[1]
    x3, y3 = v3[0], v3[1]
    px, py = point[0], point[1]

    # 计算重心坐标
    w1 = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    w2 = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    w3 = 1 - w1 - w2

    # 判断点是否在三角形内部
    if 0 <= w1 <= 1 and 0 <= w2 <= 1 and 0 <= w3 <= 1:
        return True
    else:
        return False
def centroid_w(point, uv_coords):
    # 提取顶点坐标和UV坐标
    v1, v2, v3 = uv_coords
    x1, y1 = v1[0], v1[1]
    x2, y2 = v2[0], v2[1]
    x3, y3 = v3[0], v3[1]
    px, py = point[0], point[1]

    # 计算重心
    w1 = ((y2 - y3) * (px - x3) + (x3 - x2) * (py - y3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    w2 = ((y3 - y1) * (px - x3) + (x1 - x3) * (py - y3)) / ((y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3))
    w3 = 1 - w1 - w2
    return w1, w2, w3

def transform_uv_coords(uv_coords, border_scale):
    # 提取顶点坐标
    v1, v2, v3 = uv_coords
    x1, y1 = v1[0], v1[1]
    x2, y2 = v2[0], v2[1]
    x3, y3 = v3[0], v3[1]
    
    # 计算重心坐标
    centroid_x = (x1 + x2 + x3) / 3
    centroid_y = (y1 + y2 + y3) / 3
    
    # 创建变换矩阵
    transform_matrix = np.array([[border_scale, 0], [0, border_scale]])
    
    # 进行坐标变换
    transformed_coords = []
    for coord in uv_coords:
        coord_vector = np.array([[coord[0] - centroid_x], [coord[1] - centroid_y]])
        transformed_vector = np.dot(transform_matrix, coord_vector)
        transformed_coord = (transformed_vector[0] + centroid_x, transformed_vector[1] + centroid_y)
        transformed_coords.append(transformed_coord)
    
    return transformed_coords
def transform_uv_coords_by_bbox(uv_coords, border_scale):
    # 提取顶点坐标
    v1, v2, v3 = uv_coords
    x1, y1 = v1[0], v1[1]
    x2, y2 = v2[0], v2[1]
    x3, y3 = v3[0], v3[1]
    
    # 计算重心坐标
    centroid_x = (x1 + x2 + x3) / 3
    centroid_y = (y1 + y2 + y3) / 3
    
    # 创建缩放矩阵
    transform_matrix = np.array([[border_scale, 0], [0, border_scale]])
    
    # 进行坐标变换
    transformed_coords = []
    for coord in uv_coords:
        coord_vector = np.array([[coord[0] - centroid_x], [coord[1] - centroid_y]])
        transformed_vector = np.dot(transform_matrix, coord_vector)
        transformed_coord = (transformed_vector[0] + centroid_x, transformed_vector[1] + centroid_y)
        transformed_coords.append(transformed_coord)
    
    return transformed_coords

def pixelHandler(uv_coords,uv_border,img_size,vertex_color,pixels):
    image_height = img_size
    image_width = img_size
    for y in range(image_height):
        for x in range(image_width):
#            print(x,y)
            # 转换为UV坐标
            u = (x + 0.5) / image_width
            v = (y + 0.5) / image_height
            # 判断像素点是否在三角形内部
            point = (u, v)
            if is_point_inside_triangle(point, uv_border):
#                print(uv_coords)
#                print(u)
                # 将像素设置为白色
                w1, w2, w3 = centroid_w(point, uv_coords)
                color = (
                    w1 * vertex_color[0][0] + w2 * vertex_color[1][0] + w3 * vertex_color[2][0],
                    w1 * vertex_color[0][1] + w2 * vertex_color[1][1] + w3 * vertex_color[2][1],
                    w1 * vertex_color[0][2] + w2 * vertex_color[1][2] + w3 * vertex_color[2][2],
                )
                # 将像素设置为插值后的颜色
                pixels[y, x] = [color[0], color[1], color[2], 1.0]
#            else:
#                pixels[y, x] = [0.0, 0.0, 0.0, 1.0]
#        print("=========")
    #faceHandler

def fillUV(uv_coords, border, color, pixels ,img_size):
    """
    :params uv_coords: 顶点色位置
    :params border: 边界范围, 大于等于顶点色范围
    :params color: 三个顶点色值
    :params img_size: 图像大小
    """
    # 坐标变换到图像范围
    border = [(x*img_size, y*img_size) for x, y in border]
    
    x1, y1 = border[0]  # 三角形顶点1的坐标
    x2, y2 = border[1]  # 三角形顶点2的坐标
    x3, y3 = border[2]  # 三角形顶点3的坐标

    x_coords, y_coords = zip(*border)  # 将 x 坐标和 y 坐标分开

    min_x = int(min(x_coords))  # x 坐标的最小值
    max_x = int(max(x_coords))  # x 坐标的最大值
    min_y = int(min(y_coords))  # y 坐标的最小值
    max_y = int(max(y_coords))  # y 坐标的最大值
    try:
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                cross_product1 = (x2 - x1) * (y - y1) - (x - x1) * (y2 - y1)
                cross_product2 = (x3 - x2) * (y - y2) - (x - x2) * (y3 - y2)
                cross_product3 = (x1 - x3) * (y - y3) - (x - x3) * (y1 - y3)
                
                if cross_product1 >= 0 and cross_product2 >= 0 and cross_product3 >= 0:
                    w1, w2, w3 = centroid_w((x/img_size,y/img_size), uv_coords)

                    # 将像素设置为插值后的颜色
                    pixels[y, x] = [w1 * color[0][0] + w2 * color[1][0] + w3 * color[2][0],
                        w1 * color[0][1] + w2 * color[1][1] + w3 * color[2][1],
                        w1 * color[0][2] + w2 * color[1][2] + w3 * color[2][2], 1]
    except Exception as e:
        print(e)

    # 遍历所有的三角面

def pointColorSaveToTex(img_size):
    wm = bpy.context.window_manager
    wm.progress_begin(0, 100)
        # 创建一个新图像
    image_width = img_size
    image_height = img_size
    image = bpy.data.images.new("UV_Imagetest", width=image_width, height=image_height)

    # 获取当前活动对象的数据
    obj = bpy.context.active_object
    mesh = obj.data

    # 确保对象是一个网格对象
    if obj.type != 'MESH':
        raise ValueError("The active object is not a mesh")
    if not obj:
        raise ValueError("No Selected OBJ")

    # 获取网格的UV数据图层
    uv_layer = mesh.uv_layers.active

    # 创建一个空白的像素数组
    pixels = np.zeros((image_width, image_height, 4), dtype=np.float32)

    for face in mesh.polygons:
        # 存储面的三个顶点的UV坐标
        uv_coords = []
        vertex_color = []
        # print("Polygon", face.index)
        wm.progress_update(int(face.index/len(mesh.polygons) * 100))
        for loop_index in face.loop_indices:
            vtx_index = mesh.loops[loop_index].vertex_index
            uv = uv_layer.data[loop_index].uv
            uv_coords.append((uv.x, uv.y))
            
            #获取对应的顶点颜色值
            
            index_color = mesh.vertex_colors.active.data[loop_index].color[:4]
            vertex_color.append((index_color[0],index_color[1],index_color[2]))
            
           # 遍历图像上的像素
        #每个面执行一次
        fillUV(uv_coords,transform_uv_coords_by_bbox(uv_coords, 1.2),vertex_color,pixels,img_size)
        #pixelHandler(uv_coords,transform_uv_coords(uv_coords, 1.2),img_size,vertex_color,pixels)
        

    # 将像素数组转换为图像数据
    pixels = pixels.flatten()
    image.pixels = pixels
           # 保存图像到相对目录下
    image_path = bpy.path.abspath("//sdfbakerTemp.png")
    image.save_render(image_path)

    try:
        # 将图像打包到blend文件中
        bpy.ops.image.pack({'active_image': image})

        # 删除临时图像文件
        bpy.ops.image.open(filepath=image_path)
        bpy.data.images.remove(image)

        # 打印成功消息
        print("Image saved and packed successfully.")
    except Exception as e:
        # 显示警告和异常信息
        print("Failed to save and pack the image.")
        print("Exception:", str(e))



 
   
