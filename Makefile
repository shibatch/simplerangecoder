CXX = g++
CXXFLAGS = -O3 -std=c++20 -fPIC -Wall -Wextra
LDFLAGS = -shared

TARGET_LIB = librangecoder.so
TARGET_TEST = test_range_coder_cpp
TARGET_HELLO = hello_world_cpp

SRCS = range_coder.cpp
OBJS = $(SRCS:.cpp=.o)

.PHONY: all test hello clean

all: $(TARGET_LIB) $(TARGET_TEST) $(TARGET_HELLO)

$(TARGET_LIB): $(OBJS)
	$(CXX) $(LDFLAGS) -o $@ $^

$(TARGET_TEST): test_range_coder.cpp range_coder.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^

$(TARGET_HELLO): hello_world.cpp range_coder.cpp
	$(CXX) $(CXXFLAGS) -o $@ $^

%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

test: $(TARGET_TEST)
	./$(TARGET_TEST)
	python3 -m unittest test_range_coder.py

hello: $(TARGET_HELLO)
	./$(TARGET_HELLO)
	python3 hello_world.py

clean:
	rm -f $(OBJS) $(TARGET_LIB) $(TARGET_TEST) $(TARGET_HELLO)
