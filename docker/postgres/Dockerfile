FROM rockylinux:9

# Install build tools and EPEL
RUN dnf install -y epel-release && \
    dnf config-manager --set-enabled crb && \
    dnf install -y gcc make git redhat-rpm-config

# Install pgEdge Enterprise Postgres 17 and pgvector
RUN dnf install -y https://dnf.pgedge.com/reporpm/pgedge-release-latest.noarch.rpm && \
    dnf install -y pgedge-enterprise-postgres_17 pgedge-pgvector_17 pgedge-postgresql17-devel

# Add PostgreSQL binaries to PATH
ENV PATH="/usr/pgsql-17/bin:${PATH}"
ENV PG_CONFIG="/usr/pgsql-17/bin/pg_config"

# Clone and build pg_semantic_cache
RUN git clone https://github.com/pgedge/pg_semantic_cache.git /tmp/pg_semantic_cache && \
    cd /tmp/pg_semantic_cache && \
    make PG_CONFIG=/usr/pgsql-17/bin/pg_config && \
    make PG_CONFIG=/usr/pgsql-17/bin/pg_config install && \
    rm -rf /tmp/pg_semantic_cache

# Initialize the database as postgres user
USER postgres
RUN /usr/pgsql-17/bin/initdb -D /var/lib/pgsql/17/data

# Configure PostgreSQL to accept local connections
RUN echo "host all all 0.0.0.0/0 trust" >> /var/lib/pgsql/17/data/pg_hba.conf && \
    echo "listen_addresses = '*'" >> /var/lib/pgsql/17/data/postgresql.conf

EXPOSE 5432

CMD ["/usr/pgsql-17/bin/postgres", "-D", "/var/lib/pgsql/17/data"]