docker cp ../api/core/rag/extractor/markdown_extractor.py docker-api-1:/app/api/core/rag/extractor/markdown_extractor.py

docker cp ../api/core/rag/extractor/markdown_extractor.py docker-worker-1:/app/api/core/rag/extractor/markdown_extractor.py


docker restart docker-api-1
docker restart docker-worker-1

curl --location --request POST 'http://localhost/v1/datasets/9f2f2bc5-5a73-47f4-aee9-9b40c0f9b0a5/document/create-by-file' \
--header 'Authorization: Bearer dataset-L0VD4mHQ30qf6k4Tp6iBZg8p' \
--form 'data={"indexing_technique":"high_quality","doc_form":"hierarchical_model","process_rule":{"mode":"hierarchical","rules":{"pre_processing_rules":[{"id":"remove_extra_spaces","enabled":true},{"id":"remove_urls_emails","enabled":true}],"segmentation":{"separator":"\\n\\n","max_tokens":1024,"chunk_overlap":0},"parent_mode":"paragraph","subchunk_segmentation":{"separator":"\\n","max_tokens":500,"chunk_overlap":0}}},"limits":{"indexing_max_segmentation_tokens_length":4000}}' \
--form 'file=@"/Users/seanzou/dev/fastPPT/output/test2.md"'

sudo docker logs -f docker-worker-1



# docker exec -it docker-api-1 cat /app/api/core/rag/extractor/markdown_extractor.py