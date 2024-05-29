
import time

import cv2
import numpy as np
from PIL import Image

from detr import Detection_Transformers

if __name__ == "__main__":
    detr = Detection_Transformers()
    #----------------------------------------------------------------------------------------------------------#
    #   mode
    #   'predict'          
    #   'video'             
    #   'fps'               
    #   'dir_predict'       
    #   'export_onnx'       
    #----------------------------------------------------------------------------------------------------------#
    mode = "dir_predict"
    #-------------------------------------------------------------------------#
    #   crop                
    #   count               
    #   crop、count work on mode='predict'
    #-------------------------------------------------------------------------#
    crop            = False
    count           = False
    #----------------------------------------------------------------------------------------------------------#
    #   video_path          
    #                       
    #   video_save_path     
    #                   
    #   video_fps           
    #
    #   video_path、video_save_path and video_fps work on mode='video'
    #----------------------------------------------------------------------------------------------------------#
    video_path      = 0
    video_save_path = ""
    video_fps       = 25.0
    #----------------------------------------------------------------------------------------------------------#
    #   test_interval       
    #   fps_image_path      
    #   
    #   test_interval and fps_image_path work on mode='fps'
    #----------------------------------------------------------------------------------------------------------#
    test_interval   = 100
    fps_image_path  = "img/street.jpg"
    #-------------------------------------------------------------------------#
    #   dir_origin_path     
    #   dir_save_path       
    #   
    #   dir_origin_path和dir_save_path work on mode='dir_predict'
    #-------------------------------------------------------------------------#
    dir_origin_path = "img/"
    dir_save_path   = "img_out/"
    #-------------------------------------------------------------------------#
    #   simplify            
    #   onnx_save_path      
    #-------------------------------------------------------------------------#
    simplify        = True
    onnx_save_path  = "model_data/models.onnx"

    if mode == "predict":
        
        while True:
            img = input('Input image filename:')
            try:
                image = Image.open(img)
            except:
                print('Open Error! Try again!')
                continue
            else:
                r_image = detr.detect_image(image, crop = crop, count=count)
                r_image.show()

    elif mode == "video":
        capture = cv2.VideoCapture(video_path)
        if video_save_path!="":
            fourcc  = cv2.VideoWriter_fourcc(*'XVID')
            size    = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            out     = cv2.VideoWriter(video_save_path, fourcc, video_fps, size)

        ref, frame = capture.read()
        if not ref:
            raise ValueError("未能正确读取摄像头（视频），请注意是否正确安装摄像头（是否正确填写视频路径）。")

        fps = 0.0
        while(True):
            t1 = time.time()
            
            ref, frame = capture.read()
            if not ref:
                break
            
            frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            
            frame = Image.fromarray(np.uint8(frame))
            
            frame = np.array(detr.detect_image(frame))
            
            frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
            
            fps  = ( fps + (1./(time.time()-t1)) ) / 2
            print("fps= %.2f"%(fps))
            frame = cv2.putText(frame, "fps= %.2f"%(fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            cv2.imshow("video",frame)
            c= cv2.waitKey(1) & 0xff 
            if video_save_path!="":
                out.write(frame)

            if c==27:
                capture.release()
                break

        print("Video Detection Done!")
        capture.release()
        if video_save_path!="":
            print("Save processed video to the path :" + video_save_path)
            out.release()
        cv2.destroyAllWindows()
        
    elif mode == "fps":
        img = Image.open(fps_image_path)
        tact_time = detr.get_FPS(img, test_interval)
        print(str(tact_time) + ' seconds, ' + str(1/tact_time) + 'FPS, @batch_size 1')

    elif mode == "dir_predict":
        import os

        from tqdm import tqdm

        img_names = os.listdir(dir_origin_path)
        for img_name in tqdm(img_names):
            if img_name.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff')):
                image_path  = os.path.join(dir_origin_path, img_name)
                image       = Image.open(image_path)
                r_image     = detr.detect_image(image)
                if not os.path.exists(dir_save_path):
                    os.makedirs(dir_save_path)
                r_image.save(os.path.join(dir_save_path, img_name.replace(".jpg", ".png")), quality=95, subsampling=0)
                
    elif mode == "export_onnx":
        detr.convert_to_onnx(simplify, onnx_save_path)
        
    else:
        raise AssertionError("Please specify the correct mode: 'predict', 'video', 'fps', 'export_onnx', 'dir_predict'.")
