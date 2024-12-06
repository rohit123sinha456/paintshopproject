import cv2
import time
import logging
import numpy as np
import os
import ffmpeg
import cv2
from ObjectCount import ObjectCounter

class CAMERAMODEL():
    def __init__(self):
        
        self.camera_config = {
            "dept_name": "Manufacturing",
            "camera": "Camera110",
            "region_points" : [(20, 400), (1080, 400)],
            "rtsp_url" : "rtsp://localhost:18554/mystream"
        }
        self.counter = ObjectCounter(
            show=False,  # Display the output
            region=self.camera_config['region_points'],  # Pass region points
            model="yolo11n.pt",  # model="yolo11n-obb.pt" for object counting using YOLO11 OBB model.
            # classes=[0, 2],  # If you want to count specific classes i.e person and car with COCO pretrained model.
            show_in=False,  # Display in counts
            show_out=False,  # Display out counts
            verbose=False
            # line_width=2,  # Adjust the line width for bounding boxes and text display
        )
        logging.basicConfig(filename=self.camera_config['camera']+'.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.camera_config['camera'])
        #self.camera_config = camera_config
        self.rtsp_url = self.camera_config['rtsp_url']
        self.img_folder = self.camera_config['camera']
        
        self.args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"}
        try:
            self.logger.info("Begin Probing RTSP Stream for camera :- {}".format(self.rtsp_url))
            self.logger.info("Begin Probing RTSP Stream with url :- {}".format(self.img_folder))
            probe = ffmpeg.probe(self.rtsp_url,**self.args)
            cap_info = next(x for x in probe['streams'] if x['codec_type'] == 'video')
            self.logger.info("fps: {}".format(cap_info['r_frame_rate']))
            self.width = cap_info['width']          
            self.height = cap_info['height']
            self.logger.info(self.width,self.height)
            up, down = str(cap_info['r_frame_rate']).split('/')
            self.fps = eval(up) / eval(down)
            self.logger.info(f"fps: {self.fps} and height:-{self.height} and width:- {self.width}")   
        except Exception as e:
            self.logger.error("Failed to Probe RTSP Stream")
            self.logger.error(e)
            raise e
        
        if not os.path.exists(self.img_folder):
            os.makedirs(self.img_folder)

    def enqueue_frame_buffer(self):
        self.process1 = (
            ffmpeg
            .input(self.rtsp_url, **self.args)
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .overwrite_output()
            .run_async(pipe_stdout=True)
        )
        frame_count = 0
        while True:
            try:
                in_bytes = self.process1.stdout.read(self.width * self.height * 3)
                if not in_bytes:
                    self.logger.info("Some Issue with reading from STDOUT")
                    time.sleep(20)
                    self.process1.terminate()
                    time.sleep(10)
                    self.process1 = (
                        ffmpeg
                        .input(self.rtsp_url, **self.args)
                        .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                        .overwrite_output()
                        .run_async(pipe_stdout=True)
                    )
                    continue
                
                Frame = (
                    np
                    .frombuffer(in_bytes, np.uint8)
                    .reshape([self.height, self.width, 3])
                )
                if Frame is not None:
                    _ = self.counter.count(Frame)
                    frame_count += 1
                    if frame_count % (self.fps * 10) == 0:
                        for key,value in self.counter.classwise_counts.items():
                            self.logger.info(f"Time: {frame_count // self.fps} seconds")
                            self.logger.info(f"Key: {key}")  # Accessing current counts
                            self.logger.info(f"Value: {value}")  # Accessing current counts


            except Exception as e:
                self.logger.error("Problem with Processing")
                self.logger.error(e)

    def run_threads(self):
        self.logger.info("running threads")
        self.enqueue_frame_buffer()

if __name__ == "__main__":

    rtspob = CAMERAMODEL()
    rtspob.run_threads()
    
    self.logger.info("=========================================")
