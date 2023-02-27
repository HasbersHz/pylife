g++ -shared -o life64.dll -fPIC -m64 .\gollybase\*.cpp
del .\base\life64.dll
move .\life64.dll .\base\life64.dll