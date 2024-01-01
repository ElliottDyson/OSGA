"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: associative_memory.py
Description: Defines the core long-term memory module for generative agents.

Note (May 1, 2023) -- this class is the Memory Stream module in the generative
agents paper. 
"""
import json



class ConceptNode: 
  def __init__(self, persona_id,
               node_id, node_count, type_count, type, depth,
               created, expiration, 
               subject, predicate, object, 
               description, embedding_key, poignancy, keywords, filling): 
    self.persona_id = persona_id
    self.node_id = node_id
    self.node_count = node_count
    self.type_count = type_count
    self.type = type # thought / event / chat
    self.depth = depth

    self.created = created
    self.expiration = expiration
    self.last_accessed = self.created

    self.subject = subject
    self.predicate = predicate
    self.object = object

    self.description = description
    self.embedding_key = embedding_key
    self.poignancy = poignancy
    self.keywords = keywords
    self.filling = filling

  def to_cypher(self):
      """ Create a Cypher query for this node. """
      data = self.__dict__.copy()
      for key, value in data.items():
          if isinstance(value, set):
              data[key] = list(value)
          elif key == 'filling' and isinstance(value, list) and any(isinstance(i, list) for i in value):
              data[key] = json.dumps(value)  # Convert array of arrays to JSON string

      return (
          "CREATE (n:ConceptNode {persona_id: $persona_id, node_id: $node_id, node_count: $node_count, type_count: $type_count, "
          "type: $type, depth: $depth, created: $created, expiration: $expiration, last_accessed: $last_accessed, "
          "subject: $subject, predicate: $predicate, object: $object, description: $description, "
          "embedding_key: $embedding_key, poignancy: $poignancy, keywords: $keywords, filling: $filling})"
      ), data


  def spo_summary(self): 
    return (self.subject, self.predicate, self.object)