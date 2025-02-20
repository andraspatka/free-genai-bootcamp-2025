# Lang importer technical spec

The prototype of the language learning app is built, but we need to quickly populate the application with word and word groups so students can begin testing the system.

There is currently no interface for manually adding words or words groups and the process would be too tedious. 

The words and word groups should be generated out in the following way: The file name contains the word group and the file contains the words and their italian translation in JSON format e.g. adjectives.json:
```
[
    {
        "english": "cheap",
        "italian": "economico"
    },
    {
        "english": "large",
        "italian": "grande"
    },
    {
        "english": "fun",
        "italian": "divertente"
    }
]
```

You have been asked to:
- create an internal facing tool to generate vocab 
- Be able to export the generated vocab to json for later import

Technical Restrictions, app prototyping framework to be used:
- Streamlit

You need to use an LLM in order to generate the target words and word groups.

The LLM to use:
- Local LLM serving the model via OPEA

The application should connect to an LLM running on the following endpoint: `ollama-server:8008`
