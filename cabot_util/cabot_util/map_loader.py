# Copyright (c) 2020  Carnegie Mellon University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import rclpy
from ament_index_python.packages import get_package_share_directory
from std_msgs.msg import String
from nav2_msgs.srv import LoadMap

PACKAGE_PREFIX = 'package://'

def get_filename(url):
    mod_url = url
    if url.find(PACKAGE_PREFIX) == 0:
        mod_url = url[len(PACKAGE_PREFIX):]
        pos = mod_url.find('/')
        if pos == -1:
            raise Exception("Could not parse package:// format into file:// format for "+url)

        package = mod_url[0:pos]
        mod_url = mod_url[pos:]
        package_path = get_package_share_directory(package)

        mod_url = package_path + mod_url;
    return mod_url

def map_filename_callback(msg):
    global g_node, current_map_filename
    if current_map_filename != msg.data:
        current_map_filename = msg.data
        load_map(current_map_filename)

def load_map(url):
    global g_node
    filename = get_filename(url)
    g_node.get_logger().info(filename)

    servers = g_node.get_parameter('map_servers').get_parameter_value().string_array_value
    
    g_node.get_logger().info(str(servers))

    for server in servers:
        cli = g_node.create_client(LoadMap, server+'/load_map')
        req = LoadMap.Request()
        req.map_url = filename  ## need to specify file path not url
        
        if cli.wait_for_service(timeout_sec=10.0):
            g_node.get_logger().info(server + ' service is ready')
            future = cli.call_async(req)
        else:
            g_node.get_logger().info(server + ' service is not available')

def main(args=None):
    global g_node, current_map_filename
    
    current_map_filename = None
    rclpy.init(args=args)

    g_node = rclpy.create_node('map_loader')

    g_node.declare_parameter('map_servers', ['/map_server'])

    subscription = g_node.create_subscription(String, 'current_map_filename', map_filename_callback, 10)
    subscription  # prevent unused variable warning

    try:
        rclpy.spin(g_node)
    except KeyboardInterrupt:
        pass

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    g_node.destroy_node()
    rclpy.shutdown()    

if __name__ == '__main__':
    main()


