CXX = g++
CXXFLAGS = -Wall -Wno-unused-result -Og -g -std=c++17
CXXLIBS = -lgtest_main -lgtest -lpthread
HEADERDIR = ../../include/
SRCDIR = ../../src/

OBJ = utils.o

TARGET = main

.PHONY:
all: $(TARGET)

%.o: $(SRCDIR)%.cpp $(HEADERDIR)%.h
	$(CXX) $(CXXFLAGS) -I$(HEADERDIR) -c -o $@ $<

$(TARGET).o: $(TARGET).cpp
	$(CXX) $(CXXFLAGS) -I$(HEADERDIR) -c -o $@ $<

$(TARGET): $(OBJ) $(TARGET).o
	$(CXX) $(CXXFLAGS) -I$(HEADERDIR) -o $@ $^ $(CXXLIBS)

clean:
	rm -f $(OBJ) $(TARGET) $(TARGET).o
