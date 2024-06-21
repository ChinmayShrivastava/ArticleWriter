PROMPT_TO_EXTRACT_TRIPLETS = (
    "Some text is provided below related to <<topic>>. Given the text, to better understand <<requirement>>, extract up to "
    "<<num_triplets>> "
    "knowledge triplets in the form of (parent_topic, relation_type, topic). Avoid stopwords.\n"
    "---------------------\n"
    "Example:"
    "Text: <<FIRST_CHUNK_EX>>"
    "Triplets:\n"
    "<<FIRST_CHUNK_TRIPLETS>>\n"
    "Text: <<SECOND_CHUNK_EX>>"
    "Triplets:\n"
    "<<SECOND_CHUNK_TRIPLETS>>\n"
    "---------------------\n"
    "Text: {text}\n"
    "Triplets:\n"
)

PROMPT_TO_GENERATE_RESPONSES = (
    "Some information on <<topic>> is provided below. The information is of the form (parent_topic, relation_type, topic). "
    "Answer the user query using the information provided.\n"
    "---------------------\n"
    "<<triplets>>\n"
    "---------------------\n"
    "User query: <<query>>\n"
    "Response: "
)

PROMPT_TO_UPDATE_STATE = (
    "Below are some relations in the form of triplets provided from a datastore.\n"
    "The form of the triplet is (parent topic, relationship, sub topic).\n"
    "The information is verified information on topics related to {topic}.\n"
    "--------------------------------\n"
    "{triplets}\n"
    "--------------------------------\n"
    "The user input some information.\n"
    "Based on the user input, return the triplet ids in the form of a list of ids (List[ids]) from the above list that the user learned.\n"
    "These triplets should be from the above list and represent information contained inthe user input.\n"
    "--------------------------------\n"
    "User Input: {user_input}\n"
    "Answer: \n"
)