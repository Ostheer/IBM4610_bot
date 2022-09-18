#include <iostream>
#include <string>
#include <fstream>
#include <stdlib.h>

using namespace std;

int main(){
	ofstream myfile;
	myfile.open ("/home/>>>USERNAME<<</.config/suremark_pipe/buffer/toprint.txt");

	while (!cin.eof())
	{	
		string line;
		getline(cin, line);
		if (cin.fail())
		{
	        	//error
		        break;
		}
		myfile << line << endl;
	}
	
	myfile.close();
	system("/home/>>>USERNAME<<</.config/suremark_pipe/send_file > /dev/null 2>&1 &");
	return 0;
}

