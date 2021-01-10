#include <iostream>
#include <string>
#include <fstream>
#include <stdlib.h>

using namespace std;

int main(){
	ofstream myfile;
	myfile.open ("/home/ostheer/.tg_bot_read_dir/toprint.txt");

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
	system("/home/ostheer/.tg_bot_read_dir/send_file > /dev/null 2>&1 &");
	return 0;
}
