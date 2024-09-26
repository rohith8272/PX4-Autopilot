
#!/bin/bash
# Run a single instance of the 'px4' binary with a specific port.
# If -o is passed, show the output in the terminal.
# If -p <port> is passed, set a custom jmavsim port.
# If -h <0|1> is passed, set HEADLESS=0 (GUI) or HEADLESS=1 (headless mode).
# If -i <instance> is passed, set the PX4 instance number (sitl_num).

# ./sitl_run_jmavsim.sh -o -h 1 -i 2 -p 4570


# Default values
sitl_num=0   # Default instance number
show_output=false
custom_port=3434
headless=0   # Default to non-headless (GUI)

# Parse options (-o for output, -p for custom port, -h for headless mode, -i for instance number)
while getopts "op:h:i:" opt; do
  case $opt in
    o)
      show_output=true
      ;;
    p)
      custom_port=$OPTARG
      ;;
    h)
      headless=$OPTARG
      ;;
    i)
      sitl_num=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Script directory and source path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
src_path="$SCRIPT_DIR/../../"

build_path=${src_path}/build/px4_sitl_default

# Kill any running instances of px4
echo "killing running instances"
pkill -x px4 || true
sleep 1

# Set the PX4_SIM_MODEL environment variable
export PX4_SIM_MODEL=gazebo-classic_iris
export HEADLESS=$headless  # Set HEADLESS=1 or 0 based on user input

# Compute default port based on the sitl_num (port = 4560 + sitl_num - 1)
default_port=$((4560 + sitl_num - 1))
# If a custom port is provided with -p, use it. Otherwise, use the default port.
port=${custom_port:-$default_port}

# Start the PX4 instance
working_dir="$build_path/instance_$sitl_num"
[ ! -d "$working_dir" ] && mkdir -p "$working_dir"

# Switch to the working directory
pushd "$working_dir" &>/dev/null

# Display startup information
echo "starting instance $sitl_num on port $port in $(pwd) with HEADLESS=$HEADLESS"

cmd="HEADLESS=$headless $build_path/bin/px4 -i $sitl_num -d \"$build_path/etc\""
echo "Executing command: $cmd"

# Execute the px4 binary, either showing output in the terminal or redirecting it to log files
if [ "$show_output" = true ]; then
  # Show output in the terminal
  HEADLESS=$headless $build_path/bin/px4 -i $sitl_num -d "$build_path/etc"
else
  # Redirect output to log files
  HEADLESS=$headless $build_path/bin/px4 -i $sitl_num -d "$build_path/etc" >out.log 2>err.log &
fi

# Return to the original directory
popd &>/dev/null
