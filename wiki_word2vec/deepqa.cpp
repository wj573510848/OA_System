#include <cstdio>
#include <cstdlib>
#include <csignal>
#include <iostream>
#include <argtable2.h>
#include <string.h>
#include <json/json.h>
#include "faq.h"
#include "dsem.h"
#include "semqa.h"
#include "utility.h"

#define EXIT_ERROR(X) printf("%s\n", X);arg_freetable(argtable,sizeof(argtable)/sizeof(argtable[0]));return 1;

using namespace std;

/**
 * \var g_run
 * \brief Running state of the program.
 */
static volatile bool g_run = false; //static静态全局变量 volatile类型修饰符。 程序的运行状态？

/**
 * \brief Signal management.
 * \param code signal code
 */
static void signal_handler(int code) //信号处理。
{
  switch(code)
  {
    case SIGINT:
    case SIGTERM:
      g_run = false;
      break;
    default:
      break;
  }
}

static string DeepQA(const std::string& scene, const std::string& text)
{
	double faq_prob = 0.0;
	std::string semproc_res = "";
	Json::Value response = Json::Value::null;
	Json::FastWriter writer;

	std::string result = (text.empty() ? "" : faq_search(text.c_str(), &faq_prob));  //c_str:返回当前字符串的首字符地址.

#if 1
	//add semqa part
	if(!text.empty())
	{
		const char *temp_res = DSemProc(text.c_str(), 0, 5000, "182.92.160.8:8888");
		semproc_res = ((temp_res && *temp_res) ? temp_res : "");
		Json::Reader reader;
		Json::Value root;
		bool parsing = false;
		if(!semproc_res.empty()) parsing = reader.parse(semproc_res, root);
		if(parsing && root.isMember("_topics") && root["_topics"].isArray() && root["_topics"][0].isMember("_score"))
		{
			std::string topic = root["_topics"][0].isMember("_name") ? root["_topics"][0]["_name"].asString() : "";
			std::string slotval_pair = "";
			std::string slotval_pair_alter = "";
			response["_topic"]["_name"] = topic;
			response["_topic"]["_score"] = root["_topics"][0]["_score"].asInt();
			if(root["_topics"][0].isMember("_interpretations") && root["_topics"][0]["_interpretations"].isArray() && root["_topics"][0]["_interpretations"][0].isMember("_slots") && root["_topics"][0]["_interpretations"][0]["_slots"].isArray())
			{
				int i = 0;
				for(int s = 0; s < root["_topics"][0]["_interpretations"][0]["_slots"].size(); s++)
				{
					std::string _name = root["_topics"][0]["_interpretations"][0]["_slots"][s].isMember("_name") ? root["_topics"][0]["_interpretations"][0]["_slots"][s]["_name"].asString() : "";
					std::string _value = root["_topics"][0]["_interpretations"][0]["_slots"][s].isMember("_value") ? root["_topics"][0]["_interpretations"][0]["_slots"][s]["_value"].asString() : "";
					if(_name.empty() || _value.empty()) continue;
					slotval_pair += _name + "=" + _value + ";";
					slotval_pair_alter = "KEY_WORD=" + _value + ";";
					response["_topic"]["_slots"][i]["_name"] = _name;
					response["_topic"]["_slots"][i++]["_value"] = _value;
				}
			}

			if(result.empty() || faq_prob < 0.8)
			{
				result = semqa_search(topic, slotval_pair);
				if(result.empty() && !slotval_pair_alter.empty())
					result = semqa_search("Baike_Query", slotval_pair_alter);
			}
		}
	}
#endif

	response["_question"] = text;
	if(!response.isMember("_topic") && result.empty())
	{
		response["_rc"] = 1;
		response["_error"]["_code"] = "2001";
		response["_error"]["_message"] = "no result";
	}
	else
	{
		response["_rc"] = 0;
		if(!result.empty()) response["_answer"]["_text"] = result;
	}

	return writer.write(response);
}

int main(int argc, char *argv[])
{
    struct arg_lit *help            = arg_lit0("h","help", "print this help and exit");
    struct arg_str *faq_model       = arg_str0(NULL, "faq_model", "<faq_model.dat>", "faq list file");
    struct arg_str *input           = arg_str0(NULL, "input", "<input.txt>", "input file");
    struct arg_str *output          = arg_str0(NULL, "output", "<output.txt>", "output file");
    struct arg_end *end             = arg_end(20);
    void* argtable[] = { help, faq_model, input, output, end };
	char *buffer, *p_one_line;
	int buffer_len;
	FILE *outfp;

    if (arg_parse(argc,argv,argtable) > 0)
    {
        arg_print_errors(stderr, end, argv[0]);
        arg_freetable(argtable,sizeof(argtable)/sizeof(argtable[0]));
        return 1;
    }

    if (help->count > 0 || argc == 1)
    {
        printf("Usage: %s ", argv[0]);
        arg_print_syntax(stdout,argtable,"\n"); printf("\n");
        arg_print_glossary_gnu(stdout, argtable);
        arg_freetable(argtable,sizeof(argtable)/sizeof(argtable[0]));
        return 0;
    }

	if(faq_model->count == 0 || input->count == 0 || output->count == 0)
	{
		EXIT_ERROR("Invalid arguments")
	}

	faq_load(faq_model->sval[0]);

	buffer = binary_read_file_to_buffer((char *)input->sval[0], &buffer_len);
	if(NULL == buffer) 
	{
		EXIT_ERROR("Invalid input file")
	}

	outfp = fopen(output->sval[0], "wb");
	if(NULL == outfp) 
	{
		EXIT_ERROR("Invalid output file")
	}

	while (p_one_line = read_buffer_line(buffer))
	{
		string result = DeepQA("", p_one_line);
		fprintf(outfp, "input = %s\noutput = %s\n\n\n", p_one_line, result.empty() ? "" : result.c_str());
	}
	fclose(outfp);
	free(buffer);

	faq_free();

	return 0;
}