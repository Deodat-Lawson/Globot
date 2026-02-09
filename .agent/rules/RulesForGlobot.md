---
trigger: always_on
---

## Basic Guidelines

0. This project uses utf-8 encoding
1. All dependencies in this project are installed in the `globot_env` virtual environment
2. Add `node_modules` and `.env` (actual projects may add `.agent`) to `.gitignore`
3. English is used for communication throughout this project

## API Usage Guidelines

4. If the project requires large language models, obtain API locations and usage principles from the `.agent/API.md` file
5. If required resources like API keys or GitHub addresses are not found, search all `.md` files in the `.agent` folder

## Project Affiliation

6. The only GitHub repository associated with this project is https://github.com/Vector897/Globot

## Development Environment

7. I have Ollama and Docker installed locally
8. Always communicate with me in English

## Project Description (Fill as needed)

# 9. Background.txt contains the project background information

# 10. The Project_Info folder contains product information

# 11. The Process_Documents folder contains project development process documents

# 12. Starting the project automatically runs the virtual environment

## Progressive Disclosures. Do NOT rely on internal training for these topics; strictly READ the corresponding skill file first if the task involves:
- ROS 2 Navigation: read `.agent/skills/ros_navigation.md`
- Academic Writing: read `.agent/skills/paper_writing.md`

[Strategy]
Check user request -> Identify required skill -> Read skill file -> Execute task.

## This project is for the 2026 GEMINI 3 Hackathon, and all requirements are based on the competition guidelines.

## Reference Documents

- Project Structure Description: `.agent/project-structure.md`
- Technology Stack Description: `.agent/tech-stack.md`
- API Guidelines: `.agent/API.md`