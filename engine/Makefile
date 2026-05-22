CXX = g++
CXXFLAGS = -std=c++11 -Iinclude -I/usr/include/nlohmann
LDFLAGS = -lportaudio -lwebsockets -lsndfile -lSoundTouch -lm

SRC_DIR = src
OBJ_DIR = obj
BIN = cdc_engine

SRCS = $(wildcard $(SRC_DIR)/*.cpp)
OBJS = $(SRCS:$(SRC_DIR)/%.cpp=$(OBJ_DIR)/%.o)

all: $(BIN)

$(BIN): $(OBJS)
	$(CXX) -o $@ $^ $(LDFLAGS)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
	@mkdir -p $(OBJ_DIR)
	$(CXX) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -rf $(OBJ_DIR) $(BIN)

.PHONY: all clean
