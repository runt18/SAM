CREATE TABLE If NOT EXISTS ds_{id}_Syslog
(entry             INT UNSIGNED NOT NULL AUTO_INCREMENT
,src               INT UNSIGNED NOT NULL
,srcport           INT NOT NULL
,dst               INT UNSIGNED NOT NULL
,dstport           INT NOT NULL
,timestamp         TIMESTAMP NOT NULL
,protocol          CHAR(8) NOT NULL
,bytes_sent        INT NOT NULL
,bytes_received    INT
,packets_sent      INT NOT NULL
,packets_received  INT
,duration          INT NOT NULL
,CONSTRAINT PK{id}Syslog PRIMARY KEY (entry)
);

-- -----------------------
-- Create the Temp Link tables
-- -----------------------
CREATE TABLE IF NOT EXISTS ds_{id}_staging_Links
(src               INT UNSIGNED NOT NULL
,dst               INT UNSIGNED NOT NULL
,port              INT NOT NULL
,protocol          CHAR(8) NOT NULL
,timestamp         TIMESTAMP NOT NULL
,links             INT DEFAULT 1
,bytes_sent        INT NOT NULL
,bytes_received    INT
,packets_sent      INT NOT NULL
,packets_received  INT
,duration          INT NOT NULL
,CONSTRAINT PK{id}tLinks PRIMARY KEY (src, dst, port, protocol, timestamp)
);

-- -----------------------
-- Create the Link tables
-- -----------------------
CREATE TABLE IF NOT EXISTS ds_{id}_Links
(src               INT UNSIGNED NOT NULL
,dst               INT UNSIGNED NOT NULL
,port              INT NOT NULL
,protocol          CHAR(8) NOT NULL
,timestamp         TIMESTAMP NOT NULL
,links             INT DEFAULT 1 NOT NULL
,bytes_sent        INT NOT NULL
,bytes_received    INT
,packets_sent      INT NOT NULL
,packets_received  INT
,duration          INT NOT NULL
,CONSTRAINT PK{id}Links PRIMARY KEY (src, dst, port, protocol, timestamp)
);

CREATE TABLE IF NOT EXISTS ds_{id}_LinksIn
(src_start         INT UNSIGNED NOT NULL
,src_end           INT UNSIGNED NOT NULL
,dst_start         INT UNSIGNED NOT NULL
,dst_end           INT UNSIGNED NOT NULL
,protocols         VARCHAR(1024)
,port              INT NOT NULL
,timestamp         TIMESTAMP NOT NULL
,links             INT DEFAULT 1
,bytes             INT NOT NULL
,packets           INT NOT NULL
,CONSTRAINT PK{id}LinksIn PRIMARY KEY (src_start, src_end, dst_start, dst_end, port, timestamp)
,CONSTRAINT FK{id}LinksInSrc FOREIGN KEY (src_start, src_end) REFERENCES Nodes (ipstart, ipend)
,CONSTRAINT FK{id}LinksInDst FOREIGN KEY (dst_start, dst_end) REFERENCES Nodes (ipstart, ipend)
);

CREATE TABLE IF NOT EXISTS ds_{id}_LinksOut
(src_start         INT UNSIGNED NOT NULL
,src_end           INT UNSIGNED NOT NULL
,dst_start         INT UNSIGNED NOT NULL
,dst_end           INT UNSIGNED NOT NULL
,protocols         VARCHAR(1024)
,port              INT NOT NULL
,timestamp         TIMESTAMP NOT NULL
,links             INT DEFAULT 1
,bytes             INT NOT NULL
,packets           INT NOT NULL
,CONSTRAINT PK{id}LinksOut PRIMARY KEY (src_start, src_end, dst_start, dst_end, port, timestamp)
,CONSTRAINT FK{id}LinksOutSrc FOREIGN KEY (src_start, src_end) REFERENCES Nodes (ipstart, ipend)
,CONSTRAINT FK{id}LinksOutDst FOREIGN KEY (dst_start, dst_end) REFERENCES Nodes (ipstart, ipend)
);
