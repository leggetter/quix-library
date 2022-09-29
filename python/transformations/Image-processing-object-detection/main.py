from quixstreaming import QuixStreamingClient, StreamEndType, StreamReader, AutoOffsetReset
from quixstreaming.app import App
from quix_function import QuixFunction
from image_processing import ImageProcessing
import os

# Quix injects credentials automatically to the client.
# Alternatively, you can always pass an SDK token manually as an argument.
client = QuixStreamingClient()
print("Starting")
print("Opening input and output topics")
input_topic = client.open_input_topic(os.environ.get("input"), "processing3", auto_offset_reset=AutoOffsetReset.Latest)
output_topic = client.open_output_topic(os.environ.get("output"))
image_processor = ImageProcessing()

# Callback called for each incoming stream
def read_stream(input_stream: StreamReader):
    # Create a new stream to output data
    output_stream = output_topic.create_stream(input_stream.stream_id)
    output_stream.properties.parents.append(input_stream.stream_id)

    # handle the data in a function to simplify the example
    quix_function = QuixFunction(output_stream, image_processor)

    # React to new data received from input topic.
    input_stream.parameters.on_read += quix_function.on_parameter_data_handler

    # When input stream closes, we close output stream as well.
    def on_stream_close(endType: StreamEndType):
        output_stream.close()
        print("Stream closed:" + output_stream.stream_id)

    input_stream.on_stream_closed += on_stream_close


# Hook up events before initiating read to avoid losing out on any data
input_topic.on_stream_received += read_stream

# Hook up to termination signal (for docker image) and CTRL-C
print("Listening to streams. Press CTRL-C to exit.")

# Handle graceful exit of the model.
App.run()
