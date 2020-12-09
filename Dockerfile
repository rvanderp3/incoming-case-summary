FROM registry.redhat.io/ubi8/python-38
EXPOSE 8000
CMD ["python", "-m", "http.server", "8000"]
