import os
import subprocess
import argparse
import sys

# Set up argument parser
parser = argparse.ArgumentParser(description='Run PX4 SITL with custom parameters.')
parser.add_argument('--client_ip', type=str, default='127.0.0.1', help='Client IP address')
parser.add_argument('--custom_port', type=int, default=12345, help='Custom port for MAVLink communication')
parser.add_argument('--input_port', type=int, default=14550, help='Input port for MAVLink communication')
parser.add_argument('--lat', type=float, default=28.452386, help='Home latitude')
parser.add_argument('--lon', type=float, default=-13.867138, help='Home longitude')
parser.add_argument('--alt', type=float, default=28.5, help='Home altitude')
parser.add_argument('--instance', type=int, default=1, help='Instance for MAVLink communication')

# Parse arguments
args = parser.parse_args()

# Set environment variables
os.environ['PX4_HOME_LAT'] = str(args.lat)
os.environ['PX4_HOME_LON'] = str(args.lon)
os.environ['PX4_HOME_ALT'] = str(args.alt)
os.environ['HEADLESS'] = '1'

# Run the PX4 SITL command


# Change directory to Tools/simulation
simulation_dir = './Tools/simulation'
os.chdir(simulation_dir)

print(f"Current working directory after change: {os.getcwd()}")

# Ensure the script is executable
subprocess.run(['chmod', '+x', 'sitl_run_jmavsim.sh'])
px4_cmd = ['./sitl_run_jmavsim.sh', '-o', '-i', str(args.instance)]

# Calculate the correct jmavsim port 
jport = 4560 + args.instance

# Prepare the jmavsim command
jmav_cmd = f'HEADLESS=1 ./jmavsim_run.sh -p {jport} -l'

try:
    # Start the PX4 SITL process
    process_px4 = subprocess.Popen(px4_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in iter(process_px4.stdout.readline, ''):
        sys.stdout.write(line)
        if "[simulator_mavlink] Waiting for simulator" in line:
                print("PX4 started and awaiting jmavsim connection")
                break

    # Change directory to jmavsim
    jmavsim_dir = './jmavsim'
    os.chdir(jmavsim_dir)
    print(f"Current working directory after change: {os.getcwd()}")

    # Start jmavsim with the calculated port
    process_jmavsim = subprocess.Popen(jmav_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in iter(process_jmavsim.stdout.readline, ''):
        sys.stdout.write(line)
        if "GUI not enabled" in line:
                print("jmavsim started successfully and waiting for ML router")
                break
        
    # Create the command for MAVLink router
    route_cmd = [
        "./mavlink-routerd-glibc-x86_64",
        f"-e {args.client_ip}:{args.custom_port}",
        f"127.0.0.1:{args.input_port}"
    ]

    print(f"Executing command: {' '.join(route_cmd)}")

    with open("start.log", "wb") as f:
        routing = subprocess.Popen(
            " ".join(route_cmd),
            shell=True,
            stdout=f,
            stderr=f,
            text=True
        )
        print(f"Executed MAVLink router command -udp port {args.custom_port}")


    # forward ports to client IP
    os.chdir('../../')
    print("directory restored", os.getcwd())

        
    

except subprocess.CalledProcessError as e:
    print(f"An error occurred: {e}")

except FileNotFoundError as e:
    print(f"Directory not found: {e}")

except Exception as e:
    print(f"An unexpected error occurred: {e}")
