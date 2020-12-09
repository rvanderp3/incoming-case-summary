FROM registry.redhat.io/ubi8/python-38:latest
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]
