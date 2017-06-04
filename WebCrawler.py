import requests
import sqlite3
import codecs
import re

class Graph():
    
    scanQueue = []
    conn = sqlite3.connect('net.db')
    cur = conn.cursor()
    try:
        cur.execute("CREATE TABLE LINK_TABLE (source_id int, dest_id int)")
        cur.execute("CREATE TABLE NAME_TABLE (target text)")
        cur.execute("INSERT INTO NAME_TABLE (target) VALUES ('http://localhost')")
    except: 
        pass

    @staticmethod
    def fetch_id(target):
        result = Graph.cur.execute("SELECT rowid FROM NAME_TABLE WHERE target = ?", (target,)).fetchone()
        if result != None:
            return result[0]
        return result

    @staticmethod
    def fetch_target(target_id): 
        result = Graph.cur.execute("SELECT target FROM NAME_TABLE WHERE rowid = ?", (target_id,)).fetchone()
        if result != None:
            return result[0]
        return result

    @staticmethod
    def insert_link(source_target, dest_target):
        source_id = Graph.fetch_id(source_target)
        dest_id = Graph.fetch_id(dest_target)
        if Graph.cur.execute("SELECT * FROM LINK_TABLE WHERE source_id = ? AND dest_id = ?", (source_id, dest_target)).fetchone() == None:
            Graph.cur.execute("INSERT INTO LINK_TABLE (source_id, dest_id) VALUES (?, ?)", (source_id, dest_id))
            Graph.conn.commit()
            return True
        return False

    @staticmethod
    def insert_target(dest_target):
        if Graph.fetch_id(dest_target) == None:
            Graph.cur.execute("INSERT INTO NAME_TABLE (target) VALUES (?)", (dest_target,))
            Graph.conn.commit()
            return True
        return False

    @staticmethod
    def scan(source_target):
        response = requests.get(source_target).text                  
        return re.findall(r'https?://[^\s<>"]+', response)     
     
    @staticmethod
    def build_target():
        
        while Graph.scanQueue != []:
            source_target = Graph.fetch_target(Graph.scanQueue.pop())
            dest_targets = Graph.scan(source_target)
            if dest_targets == []:
                continue

            for dest_target in dest_targets:         
                print(dest_target)                 
                if Graph.insert_target(dest_target):
                    Graph.scanQueue.insert(0, Graph.fetch_id(dest_target))
                #Graph.insert_link(source_target, dest_target)

    @staticmethod
    def build():
        Graph.scanQueue.insert(0, 1)
        Graph.build_target()

if __name__ == "__main__":
    print("WARNING: robots.txt rules are not implemented. Use at your own risk of being blocked by domains")
    if raw_input("PROCEED? (y/n): ") != "y":
        exit()
    Graph.build()
