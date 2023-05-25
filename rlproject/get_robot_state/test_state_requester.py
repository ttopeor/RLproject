from StateRequester import StateRequester
import asyncio
import sys
import time

state_requester = StateRequester()
for i in range(10):
    observation = state_requester.get_observation()
    print(observation)
    time.sleep(1)


#how to kill the thread in the object
state_requester.stop_server()  # Set the flag to stop the server thread
time.sleep(1)  # Give some time for the thread to stop gracefully
state_requester.join_server()
sys.exit()
# async def main():
#     state_requester = StateRequester()
#     print("create object")
#     time.sleep(1)
#     await state_requester.request_cube_state()
#     print("got cube state")
#     for i in range(3):
#         state_requester.print_states()
#         print("finish print_state()")
#         time.sleep(1)
#     sys.exit()

# asyncio.run(main())

