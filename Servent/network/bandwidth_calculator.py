import time
import psutil
import speedtest


def convert_to_gbit(value):
    '''
    Input: value in bits
    Output: value in gigabits
    '''
    return value/1024./1024./1024.*8
                # Kb  # Mb  # Gb

def convert_to_mbit(value):
    '''
    Input: value in bits
    Output: value in megabits
    '''
    return value/1024./1024.*8
                # Kb  # Mb
def bandwidth_calculator(duration=5): #default is 5 seconds
    start = psutil.net_io_counters()
    time.sleep(duration)
    end = psutil.net_io_counters()

    sent = (end.bytes_sent - start.bytes_sent) / duration  # bits/sec
    recv = (end.bytes_recv - start.bytes_recv) / duration  # bits/sec

    return sent, recv
           # Upload, Download

# if __name__ == "__main__":
#     upload_bps, download_bps = bandwidth_calculator(10)
#     print(f"Upload: {convert_to_mbit(upload_bps):.2f} Mbps, Download: {convert_to_mbit(download_bps):.2f} Mbps")


#     st = speedtest.Speedtest()
#     download = st.download()
#     upload = st.upload()
#     print("Speedtest:")
#     print(f"Download: {download / 1e6:.2f} Mbps")
#     print(f"Upload: {upload / 1e6:.2f} Mbps")
