CC = g++
CFLAGS = -std=c++20 -O3 -Wall -Iinclude -I/usr/include/soundtouch
LIBS = -lportaudio -lsndfile -lSoundTouch -lwebsockets

SRCS = src/main.cpp src/audio_engine.cpp
OBJS = $(SRCS:src/%.cpp=obj/%.o)
TARGET = cdc_engine

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $^ $(LIBS)

obj/%.o: src/%.cpp
	@mkdir -p obj
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf obj $(TARGET)
