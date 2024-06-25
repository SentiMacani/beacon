import threading
import pyautogui
import keyboard
from PIL import Image
from ultralytics import YOLO
import pydirectinput    
import time
import keyboard 


def hold_character(hold_time, character, interval=0.1):
    pyautogui.write(character * int(hold_time / interval), interval=interval)

def run_bot(decision):
    # Should we use lightning/met?
    # distance_target = 1000
    if decision["start-game"]:
        print("Clicking start button after it has been found")
        pyautogui.click(decision["start-game-location"])
    elif decision["player"]:
        print("#### Pressing W after player has been found")
        #pyautogui.typewrite("a")
        keyboard.press("w")
        time.sleep(2)

# Function to take screenshots
def take_screenshot(stop_event, model):
    screenx_center = 1920/2
    screeny_center = 1080/2
    pyautogui.FAILSAFE = False

    while not stop_event.is_set():
        time.sleep(2)
        try:
            decision = {
                "start-game": False,
                "player": False,
            }

            # Take screenshot
            screenshot = pyautogui.screenshot()
            screenshot = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
            
            results = model([screenshot], conf=.75)  # return a list of Results objects
            boxes = results[0].boxes.xyxy.tolist()
            classes = results[0].boxes.cls.tolist()
            names = results[0].names
            confidences = results[0].boxes.conf.tolist()

            # Process results list
            for box, cls, conf in zip(boxes, classes, confidences):
                x1, y1, x2, y2 = box
                
                center_x = (x1+x2) / 2
                center_y = (y1+y2) / 2

                name = names[int(cls)]
                
                if name=="start-game":
                    print("Start game detected from screnshot with conf " + str(conf))
                    decision["start-game"] = True
                    decision["start-game-location"] = (center_x, center_y)
                elif name == "player" and conf>0.91:
                    print("Player detected from screnshot with conf " + str(conf))
                    decision["player"] = True
                    decision["player-location"] = (center_x, center_y)

        except Exception as e:
            print("exception raised" + e)
        
        run_bot(decision)
        

# Main function
def main():
    print(pyautogui.KEYBOARD_KEYS)
    model = YOLO('best.pt')
    stop_event = threading.Event()
    
    # Create and start the screenshot thread
    screenshot_thread = threading.Thread(target=take_screenshot, args=(stop_event, model))
    screenshot_thread.start()

    # Listen for keyboard input to quit the program
    keyboard.wait("q")

    # Set the stop event to end the screenshot thread
    stop_event.set()

    # Wait for the screenshot thread to finish
    screenshot_thread.join()

    print("Program ended.")

if __name__ == "__main__":
    main()