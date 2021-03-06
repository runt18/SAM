import SocketServer
import threading
import signal
import time
import import_paloalto
import preprocess
import dbaccess
import traceback

buffer_mutex = threading.Lock()
mem_buffer = []

syslog_size = 0
handler_server = None
handler_thread = None
shutdown_processor = threading.Event()


def thread_batch_processor():
    # loop:
    #    wait for event, with timeout
    #    check bufferSize
    #       conditionally swap buffers and do processing.
    global syslog_size
    global importer
    seconds_per_scan = 1
    max_time_between_processing = 20

    last_processing = time.time()  # time.time() is in floating point seconds
    alive = True
    while alive:
        triggered = shutdown_processor.wait(seconds_per_scan)
        if triggered:
            alive = False

        deltatime = time.time() - last_processing
        if syslog_size > 1000:
            print("CHRON: process server running batch (due to buffer cap reached)")
            preprocess_lines()
            last_processing = time.time()
        elif deltatime > max_time_between_processing and syslog_size > 0:
            print("CHRON: process server running batch (due to time)")
            preprocess_lines()
            last_processing = time.time()
        else:
            print("CHRON: waiting for time limit or a full buffer.  Time at {0:.1f}, Size at {1}".format(deltatime, syslog_size))

        # import lines in memory buffer:
        if len(mem_buffer) > 0:
            import_lines()

    print("CHRON: process server shutting down")


def store_data(lines):
    global mem_buffer
    global buffer_mutex

    # acquire lock
    with buffer_mutex:
        # append line
        mem_buffer.append(lines)
    # release lock


def import_lines():
    global mem_buffer
    global syslog_size
    global buffer_mutex

    with buffer_mutex:
        lines = mem_buffer
        mem_buffer = []

    settings = dbaccess.get_settings()
    importer = import_paloalto.PaloAltoImporter()
    importer.datasource = settings['live_dest']
    if importer.datasource is None:
        print("IMPORTER: {0} lines lost. No destination specified for live data".format(len(lines)))
    else:
        print("IMPORTER: importing {0} lines to the Syslog. ".format(len(lines)),)
        num_inserted = importer.import_string("\n".join(lines))
        syslog_size += num_inserted
        print("Syslog is now {0}".format(syslog_size))


def preprocess_lines():
    global syslog_size
    print("PREPROCESSOR: preprocessing the syslog. ({0} lines)".format(syslog_size))
    settings = dbaccess.get_settings()
    if settings['live_dest'] is None:
        print("PREPROCESSOR: No live data source specified. Check settings.")
    else:
        preprocess.preprocess_log(ds=settings['live_dest'])
    syslog_size = 0


# Request handler used to listen on the port
# Uses synchronous message processing as threading was causing database issues
class UDPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        global buffer_size
        global buffer_id

        data = self.request[0].strip()
        store_data(data)


def signal_handler(signal_number, stack_frame):
    print("\nInterrupt received.")
    shutdown()


def shutdown():
    print("Shutting down handler.")
    handler_server.shutdown()
    if handler_thread:
        handler_thread.join()
        print("Handler stopped.")
    print("Shutting down batch processor.")
    shutdown_processor.set()


if __name__ == "__main__":
    # Port and host to listen from
    HOST, PORT = "localhost", 514

    # register signals for safe shut down
    signal.signal(signal.SIGINT, signal_handler)
    handler_server = SocketServer.UDPServer((HOST, PORT), UDPRequestHandler)
    ip, port = handler_server.server_address

    # Start the daemon listening on the port in an infinite loop that exits when the program is killed
    handler_thread = threading.Thread(target=handler_server.serve_forever)
    handler_thread.start()

    print("Live Update server listening on {0}:{1}.".format(HOST, PORT))

    try:
        thread_batch_processor()
    except:
        traceback.print_exc()
        print("==>--<" * 10)
        shutdown()

    print("Server shut down successfully.")
