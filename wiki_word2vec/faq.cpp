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
#include "encoding.h"
#include "typedef.h"
#include "libseg.h"
#include "libextfilereader.h"
#include "faq.h"
#include "semqa.h"
#include <time.h>

#define MAX_STRING_LENGTH 250

static std::map<std::string, int> punc_dct; //标点
static std::map<std::string, int> stopwords_dct; //停止词
static std::map<std::string, int> superqa_idx;
static std::map<int, std::vector<std::string> > superqa_answers;
static std::map<std::string, std::set<int> > keywords_invidx;
static std::vector<std::vector<std::string> > normalqa_pairs;
static std::map<int, std::vector<std::string> > normalqa_answers;

static int __internal_load_qapairs(char *stopword_file, char *invidx_file, char *qapair_s, char *qapair_a, char *superqa_q, char *superqa_a)
{
	int file_len;
	char *p_new_line;
	char *p_question, *p_answer;
	std::vector<std::string> qaarray;

	char *file_buf = binary_read_file_to_buffer(stopword_file, &file_len);
	if(!file_buf) return 0;
	while(p_new_line = read_buffer_line(file_buf))
		stopwords_dct[p_new_line] = 1;  //读取停止词文件，得到停止词字典。
	free(file_buf);

	file_buf = binary_read_file_to_buffer(superqa_q, &file_len);
	if(!file_buf) return 0;
	p_question = p_answer = NULL;
	while(p_new_line = read_buffer_line(file_buf))
	{
		if(0 == strncmp(p_new_line, "Q: ", 3))
			p_question = p_new_line + 3;
		else if(0 == strncmp(p_new_line, "A: ", 3))
		{
			p_answer = p_new_line + 3;
			if(p_question && p_answer && *p_question && *p_answer)
				superqa_idx[p_question] = atoi(p_answer);
		}
		else
			p_question = p_answer = NULL;
	}
	free(file_buf);

	file_buf = binary_read_file_to_buffer(superqa_a, &file_len);
	if(!file_buf) return 0;
	p_question = p_answer = NULL;
	while(p_new_line = read_buffer_line(file_buf))
	{
		if(0 == strncmp(p_new_line, "Q: ", 3))
			p_question = p_new_line + 3;
		else if(0 == strncmp(p_new_line, "A: ", 3))
		{
			p_answer = p_new_line + 3;
			if(p_question && p_answer && *p_question && *p_answer)
				superqa_answers[atoi(p_question)].push_back(p_answer);
		}
		else
			p_question = p_answer = NULL;
	}
	free(file_buf);

	file_buf = binary_read_file_to_buffer(invidx_file, &file_len);
	if(!file_buf) return 0;
	p_question = p_answer = NULL;
	while(p_new_line = read_buffer_line(file_buf))
	{
		if(0 == strncmp(p_new_line, "W: ", 3))
			p_question = p_new_line + 3;
		else if(0 == strncmp(p_new_line, "I: ", 3))
		{
			p_answer = p_new_line + 3;
			if(p_question && p_answer && *p_question && *p_answer)
				keywords_invidx[p_question].insert(atoi(p_answer));
		}
		else
			p_question = p_answer = NULL;
	}
	free(file_buf);

	file_buf = binary_read_file_to_buffer(qapair_s, &file_len);
	if(!file_buf) return 0;
	p_question = p_answer = NULL;
	qaarray.clear();
	while(p_new_line = read_buffer_line(file_buf))
	{
		if(0 == strncmp(p_new_line, "Q: ", 3))
		{
			if(qaarray.size() > 1)
				normalqa_pairs.push_back(qaarray);
			qaarray.clear();
			p_question = p_new_line + 3;
			qaarray.push_back(p_question);
		}
		else if(0 == strncmp(p_new_line, "A: ", 3))
		{
			p_answer = p_new_line + 3;
			qaarray.push_back(p_answer);
		}
	}
	if(qaarray.size() > 1)
		normalqa_pairs.push_back(qaarray);
	free(file_buf);

	file_buf = binary_read_file_to_buffer(qapair_a, &file_len);
	if(!file_buf) return 0;
	p_question = p_answer = NULL;
	while(p_new_line = read_buffer_line(file_buf))
	{
		if(0 == strncmp(p_new_line, "Q: ", 3))
			p_question = p_new_line + 3;
		else if(0 == strncmp(p_new_line, "A: ", 3))
		{
			p_answer = p_new_line + 3;
			if(p_question && p_answer && *p_question && *p_answer)
				normalqa_answers[atoi(p_question)].push_back(p_answer);
		}
		else
			p_question = p_answer = NULL;
	}
	free(file_buf);

	return 1;
}

static int get_utf8_bytes(unsigned char ch)
{
	if(ch < 128) // 1 byte
	{
		return 1;
	}
	else if(ch >= 192 && ch <= 223) // 2 bytes
	{
		return 2;
	}
	else if(ch >= 224 && ch <= 239) // 3 bytes
	{
		return 3;
	}
	else if(ch >= 240 && ch <= 247) // 4 bytes
	{
		return 4;
	}
	else if(ch >= 248 && ch <= 251) // 5 bytes
	{
		return 5;
	}
	else if(ch >= 252 && ch <= 253) // 6 bytes
	{
		return 6;
	}

	return 1;
}

static std::string string_strip(const std::string& text) //去掉首尾的标点符号。
{
	int i, j;

	i = 0;
	while(i < text.length())
	{
		//int bytes = get_utf8_bytes((unsigned char)(text[i]));
		if(punc_dct[text.substr(i, 1)] == 1)
			i += 1;
		else if(i <= (text.length()-3) && punc_dct[text.substr(i, 3)] == 1)
			i += 3;
		else
			break;
	}

	j = text.length();
	while(j > 0)
	{
		//int bytes = get_utf8_bytes((unsigned char)(text[i]));
		if(punc_dct[text.substr(j-1, 1)] == 1)
			j -= 1;
		else if((j-3) >= 0 && punc_dct[text.substr(j-3, 3)] == 1)
			j -= 3;
		else
			break;
	}

	if(i >= j) return "";

	return text.substr(i, j-i);
}

static void filter_out_puncs(char *input)
{
	int i;
	unsigned char ch1, ch2;
	char *dest = input;
	for(i = 0; i < strlen(input);)
	{
		ch1 = (unsigned char)(*(input+i));
		if(ch1 < 0x80) //ASCII character
		{
			if(ch1 != '!' && ch1 != ',' && ch1 != '?' && ch1 != ':' && ch1 != ';' && ch1 != '(' && ch1 != ')' && ch1 != '\"' && ch1 != '\'')
				*dest++ = ch1;
			i++;
		}
		else
		{
			char temp[3];
			ch2 = (unsigned char)(*(input+i+1));
			temp[0] = ch1; temp[1] = ch2; temp[2] = '\0';
			if(strcmp(temp, "。") != 0 && strcmp(temp, "，") != 0 && strcmp(temp, "！") != 0 && strcmp(temp, "？") != 0 && strcmp(temp, "：") != 0 && strcmp(temp, "；") != 0 && strcmp(temp, "…") != 0 && 
				strcmp(temp, "、") != 0 && strcmp(temp, "（") != 0 && strcmp(temp, "）") != 0 && strcmp(temp, "“") != 0 && strcmp(temp, "”") != 0 && strcmp(temp, "‘") != 0 && strcmp(temp, "’") != 0)
			{
				*dest++ = ch1;
				*dest++ = ch2;
			}
			i += 2;
		}
	}
	*dest = '\0';
}

static char* seg_exec_utf8(char *utf8, int *ovector, int ovcount)
{
	int *segres_vector = NULL;
	char *gb2312 = Utf8ToGB2312(utf8);  //utf8转换为gb2321
	int len = strlen(gb2312);           //句子的长度
	int i, j;
	char *out = NULL;

	if(len < 1) return NULL;

	segres_vector = (int *)malloc((2*len+10)*sizeof(int));
	out = (char *)malloc(3*len+10);
	if(!gb2312 || !(*gb2312) || !segres_vector || !out || ovcount < 1) goto exit;  //有一项不满足就退出

	memset(out, 0, 3*len+10);  //out初始化为0
	seg_exec(gb2312, segres_vector, 2*len+10); //??分词
	i = j = 0;
	ovector[j] = 0;
	while(segres_vector[i] >= 0)
	{
		char *pconv;
		char temp_s[MAX_STRING_LENGTH]; //字符串长度最大值，250
		if(segres_vector[++i] < 0) break;
		sprintf(temp_s, "%.*s", segres_vector[i]-segres_vector[i-1], gb2312+segres_vector[i-1]);
		//lupenglupeng20140730, else error in ner tagging "导航到人民广场。"
#if 0
		if(strstr(temp_s, "。") || strstr(temp_s, "，") || strstr(temp_s, "！") || strstr(temp_s, "？") || strstr(temp_s, "：") || strstr(temp_s, "；") || strstr(temp_s, "…") || 
			strstr(temp_s, "、") || strstr(temp_s, "（") || strstr(temp_s, "）") || strstr(temp_s, "“") || strstr(temp_s, "”") || strstr(temp_s, "‘") || strstr(temp_s, "’") || 
			strstr(temp_s, "!") || strstr(temp_s, ",") || strstr(temp_s, "?") || strstr(temp_s, ":") || strstr(temp_s, ";") || strstr(temp_s, "(") || strstr(temp_s, ")") || strstr(temp_s, "\"") || strstr(temp_s, "\'"))
		{
			continue;
		}
#else
		filter_out_puncs(temp_s);
		if(!(*temp_s)) continue;
#endif
		pconv = GB2312ToUtf8(temp_s);
		strcat(out, pconv);
#if 0
		//printf("%s\n", pconv);
		{
			FILE *fp = fopen("tagging.res", "a+b");
			fprintf(fp, "%s%s | %s", (i == 1 ) ? "SEGMENTATION: " : "", pconv, (segres_vector[i+1] < 0) ? "\n" : "");
			fclose(fp);
		}
#endif
		if((j+1) < (ovcount-1))
			ovector[++j] = strlen(out);
		free(pconv);
	}
	ovector[j+1] = -1;

exit:
	if(gb2312) free(gb2312);
	if(segres_vector) free(segres_vector);

	return out;
}

static int string_split(const std::string& str, std::vector<std::string>& ret_, std::string sep = " ")
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

        if (!tmp.empty())
        {
            ret_.push_back(tmp);
            tmp.clear();
        }
    }
    return 1;
}

double compute_sent_semantics(std::vector<std::string>& input_array, std::vector<std::string>& ref_array)
{
	std::map<std::string, std::vector<int> > words_dct;

	for(int i = 0; i < input_array.size(); i++)
	{
		if(words_dct.find(input_array[i]) != words_dct.end())
			words_dct[input_array[i]][0] += 1;
		else
		{
			words_dct[input_array[i]].push_back(1);
			words_dct[input_array[i]].push_back(0);
		}
	}

	for(int i = 0; i < ref_array.size(); i++)
	{
		if(words_dct.find(ref_array[i]) != words_dct.end())
			words_dct[ref_array[i]][1] += 1;
		else
		{
			words_dct[ref_array[i]].push_back(0);
			words_dct[ref_array[i]].push_back(1);
		}
	}

	double AA = 0.0, BB = 0.0, AB = 0.0;
	for (std::map<std::string, std::vector<int> >::iterator iter = words_dct.begin(); iter != words_dct.end(); iter++)
	{
		AB += iter->second[0]*iter->second[1];
		AA += iter->second[0]*iter->second[0];
		BB += iter->second[1]*iter->second[1];
	}

	return ((double)AB)/(sqrt(AA) * sqrt(BB));
}

int faq_load(const char* szDataPath)
{
	int res = 0;

	if(ext_file_init(szDataPath) != 0 && __internal_load_qapairs("./stopwords.list", "./invidx", "./qapair.s", "./qapair.a", "./super.q", "./super.a") != 0)
	{
		res = 1;
	}
	seg_init("./base.s");
	seg_init("./name.s");
	seg_init("./nsw.r");
	semqa_load("./semqa.dat");
	ext_file_free();

	punc_dct["\x20"] = 1; //" "
	punc_dct["\x09"] = 1; //"\t"
	punc_dct["\x3B"] = 1; //";"
	punc_dct["\x2F"] = 1; //"/"
	punc_dct["\x2D"] = 1; //"-"
	punc_dct["\x2C"] = 1; //","
	punc_dct["\x2E"] = 1; //"."
	punc_dct["\x3A"] = 1; //":"
	punc_dct["\x3F"] = 1; //"?"
	punc_dct["\x21"] = 1; //"!"
	punc_dct["\xE3\x80\x81"] = 1; //"、"
	punc_dct["\xEF\xBC\x9F"] = 1; //"？"
	punc_dct["\xEF\xBC\x81"] = 1; //"！"
	punc_dct["\xEF\xBC\x8C"] = 1; //"，"
	punc_dct["\xEF\xBC\x9A"] = 1; //"："
	punc_dct["\xE3\x80\x82"] = 1; //"。"
	punc_dct["\xEF\xBC\x9B"] = 1; //"；"
	punc_dct["\xEF\xBC\x8F"] = 1; //"／"

	return res;
}

void faq_free()
{
	semqa_free();
	seg_free();
	stopwords_dct.clear();
	superqa_idx.clear();
	superqa_answers.clear();
	keywords_invidx.clear();
	normalqa_pairs.clear();
	normalqa_answers.clear();
}

const char* faq_search(const char* utf8_text, double *faq_prob)
{
#if 0    //#if 0 类似于注释。
	char *gb2312 = Utf8ToGB2312((char *)text.c_str());
	if(!gb2312) return "";
	free(gb2312);
#endif

	*faq_prob = 0.0;
	
	std::string text = utf8_text;
	std::string text_stripped = string_strip(text);
	if(text_stripped.empty()) return "";   //在首尾去掉标点符号。

	srand((unsigned)time(NULL)); //初始化随机参数。

	std::map<std::string, int>::iterator it = superqa_idx.find(text_stripped);   //生成迭代器 it 指向匹配到的第一个。
	if(it != superqa_idx.end() && superqa_answers.find(it->second) != superqa_answers.end()) //it->second 与 first 分别指字典中一组数据中的第一个与第二个。
	{
		*faq_prob = 1.0;
		return superqa_answers[it->second][rand()%(superqa_answers[it->second].size())].c_str(); //随机取得一句回答。
	}

	//move semqa to deepqa.cpp

	char *utf8_segres = NULL;
	int *segres_vector = NULL;
	segres_vector = (int *)malloc((3*text_stripped.length()+10)*sizeof(int));
	if(!segres_vector) return "";
	utf8_segres = seg_exec_utf8((char *)text_stripped.c_str(), segres_vector, 3*text_stripped.length()+10); //某种处理。。。
	if(!utf8_segres) return "";
	std::string text_segres = utf8_segres;
	free(utf8_segres);
	if(text_segres.empty()) return "";
	std::vector<std::string> input_array, input_array_nostop;
	int i = 0;
	while(segres_vector[i] >= 0)
	{
		if(segres_vector[i+1] < 0) break;
		input_array.push_back(text_segres.substr(segres_vector[i], segres_vector[i+1]-segres_vector[i]));
		if(stopwords_dct.find(input_array[i]) == stopwords_dct.end())
			input_array_nostop.push_back(input_array[i]);               //去停止词。input_array 包含停止词，input_array_nostop不包含停止词。
		i++;
	}
	free(segres_vector);

	std::set<int> intersect;
	if(1 == input_array_nostop.size()) //如果只有一个词。
	{
		for (std::set<int>::iterator iter = keywords_invidx[input_array_nostop[0]].begin(); iter != keywords_invidx[input_array_nostop[0]].end(); iter++)
			intersect.insert(*iter);
	}
	else
	{
		for(i = 0; i < input_array_nostop.size(); i++)
		{
#if 0
			{
				FILE *fp = fopen("faq.log", "a+b");
				fprintf(fp, "%s | ", input_array_nostop[i].c_str());
				if(i >= (input_array_nostop.size()-1)) fprintf(fp, "\n");
				fclose(fp);
			}
#endif
			if(!i)
				continue;
			if(1 == i)
				std::set_intersection(keywords_invidx[input_array_nostop[0]].begin(), keywords_invidx[input_array_nostop[0]].end(), keywords_invidx[input_array_nostop[1]].begin(), keywords_invidx[input_array_nostop[1]].end(), std::inserter(intersect, intersect.begin()));
			else
			{
				std::set<int> tmp = intersect;
				intersect.clear();
				std::set_intersection(keywords_invidx[input_array_nostop[i]].begin(), keywords_invidx[input_array_nostop[i]].end(), tmp.begin(), tmp.end(), std::inserter(intersect, intersect.begin()));
			}
		}
	}

	if(intersect.size() < 1) return "";

	int docid = -1;
	double max_prob = -1.0;
	for (std::set<int>::iterator iter = intersect.begin(); iter != intersect.end(); iter++)
	{
		if(*iter >= 0 && *iter < normalqa_pairs.size())
		{
			double prob;
			std::vector<std::string> ref_array;
			string_split(normalqa_pairs[*iter][0], ref_array);
			if((prob = compute_sent_semantics(input_array, ref_array)) > max_prob)
			{
				docid = *iter;
				max_prob = prob;
			}
		}
	}

	if(docid >= 0 && docid < normalqa_pairs.size() && normalqa_answers.find(atoi(normalqa_pairs[docid][1].c_str())) != normalqa_answers.end())
	{
		*faq_prob = max_prob;
		return normalqa_answers[atoi(normalqa_pairs[docid][1].c_str())][rand()%(normalqa_answers[atoi(normalqa_pairs[docid][1].c_str())].size())].c_str();
	}

	return "";
}
