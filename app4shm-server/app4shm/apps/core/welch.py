import numpy as np
from scipy.interpolate import interpn as interpn
from scipy import signal
import traceback


class ReadingDTO:
    def __init__(self, timestamp, x, y, z):
        self.timestamp = timestamp
        self.x = x
        self.y = y
        self.z = z


def calculate_welch_frequencies(lines):

    data_stream = []
    for line in lines:
        if len(line.strip()) > 0:
            parts = str(line.rstrip()).split(";")
            timestamp = int(parts[0])
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
            reading = ReadingDTO(timestamp, x, y, z)
            data_stream.append(reading)

    interpolated = interpolate_data_stream(data_stream)

    time_array = []
    x_array = []
    y_array = []
    z_array = []
    for i in interpolated:
        time_array.append(i.timestamp)
        x_array.append(i.x)
        y_array.append(i.y)
        z_array.append(i.z)
    welch_x_f, welch_x_pxx = calculate_welch_from_array(time_array, x_array)
    welch_y_f, welch_y_pxx = calculate_welch_from_array(time_array, y_array)
    welch_z_f, welch_z_pxx = calculate_welch_from_array(time_array, z_array)

    return welch_x_f.tolist(), welch_x_pxx.tolist(), welch_y_pxx.tolist(), welch_z_pxx.tolist()


# Constants and Parameters
INTERPOLATION_TYPE = 'linear'
TIME_INCREMENT = 20  # 20 ms


def interpolate_data_stream(data_stream: list[ReadingDTO]):
    data_times = []
    counter = 0
    data_x = []
    data_y = []
    data_z = []
    data_stream.sort(key=lambda x: x.timestamp)
    for i in data_stream:
        data_times.append(float(i.timestamp))
        data_x.append(i.x)
        data_y.append(i.y)
        data_z.append(i.z)
    while counter < len(data_times) - 1:
        count = data_times.count(data_times[counter])
        if count > 1:
            data_times.remove(data_times[counter])
            data_x.remove(data_x[counter])
            data_y.remove(data_y[counter])
            data_z.remove(data_z[counter])
            counter -= 1
        counter += 1
    t_start = data_times[0]
    t_end = data_times[len(data_times) - 1]
    t_interval_array = []
    start_me = t_start
    while start_me < t_end:
        t_interval_array.append(start_me)
        start_me += TIME_INCREMENT
    t_interval = np.array(t_interval_array)
    try:
        x_nd = interpn((np.array(data_times),), np.array(data_x), t_interval, INTERPOLATION_TYPE)
        y_nd = interpn((np.array(data_times),), np.array(data_y), t_interval, INTERPOLATION_TYPE)
        z_nd = interpn((np.array(data_times),), np.array(data_z), t_interval, INTERPOLATION_TYPE)
        inter_x = x_nd.tolist()
        inter_y = y_nd.tolist()
        inter_z = z_nd.tolist()
        ret_stream = []
        for i in range(0, len(t_interval)):
            ret_stream.append(ReadingDTO(
                                   timestamp=t_interval[i],
                                   x=inter_x[i],
                                   y=inter_y[i],
                                   z=inter_z[i]))
        return ret_stream
    except ValueError:
        track = traceback.format_exc()
        print(track)
        print("---------------------")
        print(data_times)
        return []


def calculate_welch_from_array(time: list[float], accelerometer_input: list[float]):
    delta_times = 0.02  # 20ms
    measuring_frequency = delta_times ** (-1)
    total_sample_number = len(time)  # measuring_frequency*len(time)
    n_segments = 3
    ls = int(np.round(total_sample_number / n_segments))
    overlap_perc = 50
    overlaped_samples = int(np.round(ls * overlap_perc / 100))
    discrete_fourier_transform_points = ls
    f, pxx = signal.welch(accelerometer_input, fs=measuring_frequency, nperseg=ls, noverlap=overlaped_samples,
                          nfft=discrete_fourier_transform_points)
    return f, pxx



    # f1 = np.reshape(f, (1, len(f)))
    # fs = 10e3
    # N = 1e5
    # amp = 2*np.sqrt(2)
    # freq = 1234
    # noise_power = 0.001 * fs / 2
    # time = np.arange(N) / fs
    # x = amp*np.sin(2*np.pi*freq*time)
    # x += np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
    # f, Pxx_den = signal.welch(x, fs, nperseg=1024)