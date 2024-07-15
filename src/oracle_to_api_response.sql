CREATE OR REPLACE FUNCTION call_llm_api(p_prompt_instructions VARCHAR2, p_data VARCHAR2, p_model VARCHAR2) RETURN VARCHAR2 IS
    l_http_request  UTL_HTTP.req;
    l_http_response UTL_HTTP.resp;
    l_response_text VARCHAR2(32767);
    l_payload       CLOB;
    l_combined_prompt VARCHAR2(32767);
    l_buffer        VARCHAR2(32767);
    l_clob          CLOB;
    l_json_response VARCHAR2(32767);
BEGIN
    -- Combine the prompt instructions and data
    l_combined_prompt := p_prompt_instructions || ' ' || p_data;

    -- Create the JSON payload
    DBMS_LOB.createtemporary(l_payload, TRUE);
    DBMS_LOB.writeappend(l_payload, LENGTH('{"prompt": "' || l_combined_prompt || '", "model": "' || p_model || '", "stream": false, "max_tokens": 10, "temperature": 0.7}'), 
                         '{"prompt": "' || l_combined_prompt || '", "model": "' || p_model || '", "stream": false, "max_tokens": 10, "temperature": 0.7}');

    -- Initialize the HTTP request
    l_http_request := UTL_HTTP.begin_request('http://172.27.128.124:11434/api/generate', 'POST', 'HTTP/1.1');
    UTL_HTTP.set_header(l_http_request, 'Content-Type', 'application/json');
    UTL_HTTP.set_header(l_http_request, 'Content-Length', LENGTH(l_payload));
    
    -- Write the payload to the HTTP request
    UTL_HTTP.write_text(l_http_request, l_payload);
    
    -- Get the response
    l_http_response := UTL_HTTP.get_response(l_http_request);
    
    -- Read the response into a CLOB
    DBMS_LOB.createtemporary(l_clob, TRUE);
    BEGIN
        LOOP
            UTL_HTTP.read_text(l_http_response, l_buffer, 32767);
            DBMS_LOB.writeappend(l_clob, LENGTH(l_buffer), l_buffer);
        END LOOP;
    EXCEPTION
        WHEN UTL_HTTP.end_of_body THEN
            NULL;
    END;
    
    -- Close the HTTP response
    UTL_HTTP.end_response(l_http_response);
    
    -- Convert CLOB response to VARCHAR2
    l_response_text := DBMS_LOB.substr(l_clob, 32767, 1);
    DBMS_LOB.freetemporary(l_clob);
    DBMS_LOB.freetemporary(l_payload);

    -- Extract the "response" field from the JSON response manually
    l_json_response := substr(l_response_text, instr(l_response_text, '"response":"') + 12);
    l_json_response := substr(l_json_response, 1, instr(l_json_response, '","') - 1);
    
    RETURN l_json_response;
EXCEPTION
    WHEN OTHERS THEN
        -- Handle exceptions
        RETURN 'Error: ' || SQLERRM;
END;
/
