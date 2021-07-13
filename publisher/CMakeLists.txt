find_package
（
……
message_generation
）
add_message_files(FILES Anesthesia.msg)
generation_messages(DEPENDENCIES std_msgs)
catkin_package(
……
CATKIN_DEPENDS ……message_runtime
)