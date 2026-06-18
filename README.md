# ai-tasks
Created for AI tasks


##Step to clone:

1. Run this to clone the repo - git clone https://github.com/kaniksharma886/ai-tasks.git

2. Open this - https://github.com/kaniksharma886/ai-tasks/releases/tag/v1.0.0 and download db.zip file. 
 - It was added becasue indexing rag db took 3 hrs and it was of 400 MB, but free github account has 100 MB limit.
 - If above link is not working download from here - https://drive.google.com/file/d/1F09A05EfMEwDLlH1kwLvQeTxo1q9ozol/view?usp=sharing

3. Save it in repo folder at root level under ai-tasks/ where all .py files are present.



##Step to run in CLI mode:

###1. Run following to set API key:

export OPENAI_API_KEY=<API Key without quotes>



###2. Task 3.1 and 3.2 (a), (b), (c)

cd ai-tasks
run "python3 chat.py"



###3. Task 3.2 (d)
cd ai-tasks
run "python3 rag_manager_test.py"



###4. Task 3.3
cd ai-tasks
run "python3 travel_agent.py"

- Due to model token limits it might get status code 429. I've added a retry.



###5. Task 3.4
cd ai-tasks
run "python3 coding_helper.py"


###6. Stretch task

	1. Update docker-compose.yml and set OPENAI_API_KEY
	2. cd ai-tasks
	3. run "docker compose up --build"
	4. open http://localhost:8001 in browser.


