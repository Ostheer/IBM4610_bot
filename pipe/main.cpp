#include <iostream>
#include <string>
#include <fstream>

using namespace std;

int main(){
	ofstream myfile;
	myfile.open ("/home/ostheer/.tg_bot_read_dir/toprint.txt");
	myfile << "<F>";

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
	
	myfile << "</F>";
	myfile.close();
	return 0;
}
