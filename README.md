# Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition (From TDPS Project)
This project focused on creating an smart robot car with autonomous capabilities to execute multiple functions. This is the visual processor part.

The task patio is illustrated as following:
![83DD9C413B10A064A603E59583D8360A](https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/0e3b9da3-92f1-41ed-bf4d-ad3b9a1f4404)

For the tasks of lane keeping, arrow recognition and traffic light recognition in the project, a vision processing subsystem based on the vision sensor OpenMV is designed. This subsystem is composed of the OpenMV vision sensor and a MCU. The integration of these components allows the subsystem to process visual information in real-time and make decisions that guide the movements of the robot.

The OpenMV vision sensor is equipped with an ARM Cortex M7 processor with 512K RAM and 256K ROM. It captures images with a resolution of 320x240 pixels and supports AI model training through Edge Impulse.

## Lane Extraction an Bias Calculation
<img width="1262" alt="截屏2024-07-11 17 28 54" src="https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/4ac3bf0d-f50a-463e-8525-b123e54d5c75">
For lane keeping, the OpenMV camera captures an image of the road, focusing on two regions of interest (ROIs) where lane boundaries are expected to appear. The images are converted to binary format using colour thresholding to highlight lane markings. The lane boundaries within each ROI are then approximated using a linear regression algorithm. The system calculates the deviation, i.e. the deviation between the detected lane centre and the vehicle centre.

However, in case that the camera lose track of one lane, the algorithm will calculated bias form one side. This deviation value is sent to the MCU via UART communication using customized protocl, enabling the MCU to adjust the steering angle of the robot to keep it in the centre of the lane.

• Step 1 Binarization (Color Thresholding): A color threshold-based binarization is implemented to convert the image into a binary format and filter out irrelevant information.
• Step 2 Region of Interest (ROI: ROI that focuses on the relevant part of the image where lanes are expected to be.reducing the amount of data to be processed. 
• Step 3 Line Regression: Using a linear regression algorithm within the ROI. The regression algorithm minimizes the distance of each white pixel within ROI and the approximate line. This method provides a reliable way to apprimate lane lines in various driving conditions. 
• Step 4 Bias Calculation: It calculates the bias, which is the deviation of the detected lane center of ROI, which is specified in Figure 3. When both lane boundaries are detected, the algorithm determines the bias from the center between them to the camera's viewpoint. If only one lane boundary is detected, the bias is calculated based on the known lane width and the position of the detected line.<img width="474" alt="截屏2024-07-11 17 32 21" src="https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/af8e662a-3ed3-42bc-9db2-8ecb76ac33e9">

## Arrow Recognition && Traffic Light Recognition
Traffic light recognition also uses the FOMO model. Specific ROI located on the right side of the screen is extracted and compressed to a resolution of 96x96 to identify traffic light states. The FOMO model analyses the image and classifies it into one of four categories: red, green, yellow and red-yellow. Each category corresponds to one traffic light state. The recognized states are sent to the MCU, which then controls the actions of the robot. For example, when a red light is recognized, the MCU controls the robot to stop, and when a green light is recognized, the MCU allows the robot to continue.<img width="1208" alt="截屏2024-07-11 17 33 38" src="https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/c3482088-dc5f-4d03-8e90-9b965c2c3afd">
<img width="1010" alt="截屏2024-07-11 17 35 27" src="https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/ee76057d-d73f-40c6-8ee8-475685fb5ba2">

## Communication Design
<img width="538" alt="截屏2024-07-11 17 34 08" src="https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/664c204c-1cfb-42b0-974a-66592156414a">
<img width="1212" alt="截屏2024-07-11 17 34 20" src="https://github.com/Juneh01/Visual-Processing-Subsystem-for-Lane-keeping-and-Recognition-TDPS-Project-/assets/172175067/da00a8e0-99a4-458c-88fc-fa3a9cc4c9b6">
Communication between the OpenMV camera and the MCU is ensured by a well-defined frame structure that ensures robust and reliable data exchange. The structure consists of a frame header and a frame tail to mark the beginning and end of the data frame, as well as multiple data fields for different sensor inputs. 
This setup ensures data integrity and incorporates error handling mechanisms to maintain constant and reliable communication. The MCU plays a key role in processing the data received from the OpenMV camera and executing the control algorithms. It implements a PID (Proportional-Integral- Derivative) control algorithm that adjusts the steering of the vehicle according to the lane keeping deviation. The control system adapts to different levels of deviation to provide precise steering control.
