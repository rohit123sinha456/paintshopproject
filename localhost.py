import cv2
import time
import logging
import numpy as np
import os
import ffmpeg
import cv2
from ObjectCount import ObjectCounter
from datetime import datetime
import requests

# from ObjectCount import ObjectCounter

class CAMERAMODEL():
    def __init__(self):
        
        self.camera_config = {
            "camera": "Camera110",
            "camera_id": int("13"),
            "region_points" : [(20, 400), (1080, 400)],
            "url":"http://localhost:8000/ai/getcampayload",
            "logdir":"D:\Rohit\Sudisa\paintshop\paintshopproject\paintai\logs",
            "rtsp_url" : "rtsp://localhost:18554/mystream"
        }
        self.counter = ObjectCounter(
            show=False,  # Display the output
            region=self.camera_config['region_points'],  # Pass region points
            model= "yolo11n.pt",  # model="yolo11n-obb.pt" for object counting using YOLO11 OBB model.
            # classes=[0, 2],  # If you want to count specific classes i.e person and car with COCO pretrained model.
            show_in=False,  # Display in counts
            show_out=False,  # Display out counts
            verbose=False
            # line_width=2,  # Adjust the line width for bounding boxes and text display
        )
        logging.basicConfig(
            filename=os.path.join(self.camera_config['logdir'],self.camera_config['camera']+'.log'), 
            level=logging.DEBUG, format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(self.camera_config['camera'])
        #self.camera_config = camera_config
        self.rtsp_url = self.camera_config['rtsp_url']
        self.update_duration = 10
        self.args = {
        "rtsp_transport": "tcp",
        "fflags": "nobuffer",
        "flags": "low_delay"}
        self.cache = {}
        try:
            self.logger.info("Begin Probing RTSP Stream for camera :- {}".format(self.rtsp_url))
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

    def send_post_request(self, json_body, headers=None):
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(self.camera_config["url"], json=json_body, headers=headers)
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            return True  # Parse and return JSON response
        except requests.exceptions.RequestException as e:
            print(f"Error sending POST request: {e}")
            return False


    def enqueue_frame_buffer(self):
        self.process1 = (
            ffmpeg
            .input(self.rtsp_url, **self.args)
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .overwrite_output()
            .run_async(pipe_stdout=True)
        )
        frame_count = 0
        starttime = datetime.now().isoformat()
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
                    if frame_count % (self.fps * self.update_duration) == 0:
                        for key,value in self.counter.classwise_counts.items():
                            try:
                                self.counter.classwise_counts["starttime"] = starttime
                                self.counter.classwise_counts["endtime"] = datetime.now().isoformat()
                                success = self.send_post_request(self.counter.classwise_counts)
                                if success:
                                    self.logger.info("Successfully sent to server")
                                else:
                                    self.logger.info("Failed sent to server")
                            except Exception as e:
                                self.logger.error("Error Sending to Server")
                                self.logger.error(e)
                        frame_count = 0
                        starttime = datetime.now().isoformat()

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
