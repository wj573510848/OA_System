#include <string.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <map>
#include <set>
#include <vector>
#include <algorithm>
#include <cmath>
#include "utility.h"
#include "semqa.h"
#include <time.h>

#define MAX_STRING_LENGTH 250

static std::map<std::string, std::vector<std::map<std::string, std::string> > > semqa_answers;
static std::map<std::string, std::map<std::string, std::set<int> > > semqa_question;

static int string_split(const std::string& str, std::vector<std::string>& ret_, std::string sep = " ", bool allow_empty = true)
{
    if (str.empty())
    {
        return 0;
    }

    std::string tmp;
    std::string::size_type pos_begin = str.find_first_not_of(sep);
    std::string::size_type sep_pos = 0;

    while (pos_begin != std::string::npos)
    {
        sep_pos = str.find(sep, pos_begin);
        if (sep_pos != std::string::npos)
        {
            tmp = str.substr(pos_begin, sep_pos - pos_begin);
            pos_begin = sep_pos + sep.length();
        }
        else
        {
            tmp = str.substr(pos_begin);
            pos_begin = sep_pos;
        }

        if (!tmp.empty() || allow_empty)
        {
            ret_.push_back(tmp);
            tmp.clear();
        }
    }

    return 1;
}


int semqa_load(const std::string& szSemQAPath)
{
	int file_len;
	char *p_new_line;
	std::vector<std::string> qaarray;

	char *file_buf = binary_read_file_to_buffer((char *)(szSemQAPath.c_str()), &file_len);
	if(!file_buf) return 0;

	std::vector<std::string> fields_array;
	while(p_new_line = read_buffer_line(file_buf))
	{
		if(0 == strncmp(p_new_line, "ref#", 4))
		{
			std::vector<std::string> line_array;
			if(0 == string_split(p_new_line, line_array, "#") || line_array.size() < 5 || line_array.size() != fields_array.size())
				continue;
			std::map<std::string, std::string > line_map;
			for(int i = 0; i < line_array.size(); i++)
				line_map[fields_array[i]] = line_array[i];
			if(line_map["topic"].empty() || line_map["standard"].empty() && line_map["brief"].empty() && line_map["complete"].empty())
				continue;
			std::map<std::string, std::string> tempAnswerMap;
			if(!line_map["standard"].empty()) tempAnswerMap["standard"] = line_map["standard"];
			if(!line_map["brief"].empty()) tempAnswerMap["brief"] = line_map["brief"];
			if(!line_map["complete"].empty()) tempAnswerMap["complete"] = line_map["complete"];
			std::vector<std::string> slot_array, value_array;
			string_split(line_map[";slot names"], slot_array, ";", false);
			string_split(line_map[";slot values"], value_array, ";", false);
			if(slot_array.size() > 0 && slot_array.size() == value_array.size())
			{
				for(int i = 0; i < slot_array.size(); i++)
				{
					semqa_question[line_map["topic"]][slot_array[i]+'='+value_array[i]].insert(semqa_answers[line_map["topic"]].size());
					tempAnswerMap[slot_array[i]] = value_array[i];
				}
			}
			else
				semqa_question[line_map["topic"]][""].insert(semqa_answers[line_map["topic"]].size());
			semqa_answers[line_map["topic"]].push_back(tempAnswerMap);
		}
		else if(0 == strncmp(p_new_line, "#ref#", 5))
		{
			if(0 == string_split(p_new_line, fields_array, "#") || fields_array.size() < 5)
				break;
		}
	}
	free(file_buf);

	return 1;
}

void semqa_free()
{
	semqa_answers.clear();
	semqa_question.clear();
}

const std::string semqa_search(const std::string& topic, const std::string& slotval_pair)
{
	if(topic.empty() || semqa_question.find(topic) == semqa_question.end() || semqa_answers.find(topic) == semqa_answers.end()) return "";
	
	srand((unsigned)time(NULL));

	if(slotval_pair.empty())
	{
		int index = rand()%semqa_answers[topic].size();
		std::string title = "";
		if(topic == "Literature_Story" && semqa_answers[topic][index].find("STORY_NAME") != semqa_answers[topic][index].end())
			title = semqa_answers[topic][index]["STORY_NAME"] + ";";
		else if(topic == "Literature_Poem" && semqa_answers[topic][index].find("POET_NAME") != semqa_answers[topic][index].end() && semqa_answers[topic][index].find("POEM_NAME") != semqa_answers[topic][index].end())
			title = semqa_answers[topic][index]["POET_NAME"] + ";" + semqa_answers[topic][index]["POEM_NAME"] + ";";
		else if(topic == "Recipe_Search" && semqa_answers[topic][index].find("RECIPE_NAME") != semqa_answers[topic][index].end())
			title = semqa_answers[topic][index]["RECIPE_NAME"] + ";";
		else if(topic == "Literature_Idiom" && semqa_answers[topic][index].find("IDIOM_NAME") != semqa_answers[topic][index].end())
			title = semqa_answers[topic][index]["IDIOM_NAME"] + ";";
		if(semqa_answers[topic][index].find("brief") != semqa_answers[topic][index].end())
			return (title+semqa_answers[topic][index]["brief"]);
		else if (semqa_answers[topic][index].find("standard") != semqa_answers[topic][index].end())
			return (title+semqa_answers[topic][index]["standard"]);
		else if (semqa_answers[topic][index].find("complete") != semqa_answers[topic][index].end())
			return (title+semqa_answers[topic][index]["complete"]);
		else
			return "";
	}

	std::set<int> intersect;
	std::vector<std::string> ref_array;
	if(0 == string_split(slotval_pair, ref_array, ";")) return "";
	int i, j;
	for(i = 0; i < ref_array.size(); i++)
	{
		if(semqa_question[topic].find(ref_array[i]) != semqa_question[topic].end())
		{
			for (std::set<int>::iterator iter = semqa_question[topic][ref_array[i]].begin(); iter != semqa_question[topic][ref_array[i]].end(); iter++)
				intersect.insert(*iter);
			break;
		}
	}
	for(j = i+1; j < ref_array.size(); j++)
	{
		if(semqa_question[topic].find(ref_array[j]) != semqa_question[topic].end())
		{
			std::set<int> tmp = intersect;
			intersect.clear();
			std::set_intersection(semqa_question[topic][ref_array[j]].begin(), semqa_question[topic][ref_array[j]].end(), tmp.begin(), tmp.end(), std::inserter(intersect, intersect.begin()));
		}
	}

	if(intersect.size() < 1) return "";

	int id = rand()%intersect.size();
	int index = 0;
	for (std::set<int>::iterator iter = intersect.begin(); iter != intersect.end(); iter++)
	{
		if(*iter >= 0 && *iter < semqa_answers[topic].size() && index == id)
		{
			if(semqa_answers[topic][*iter].find("brief") != semqa_answers[topic][*iter].end())
				return semqa_answers[topic][*iter]["brief"].c_str();
			else if (semqa_answers[topic][*iter].find("standard") != semqa_answers[topic][*iter].end())
				return semqa_answers[topic][*iter]["standard"].c_str();
			else if (semqa_answers[topic][*iter].find("complete") != semqa_answers[topic][*iter].end())
				return semqa_answers[topic][*iter]["complete"].c_str();
			else
				return "";
		}
		index++;
	}

	return "";
}
