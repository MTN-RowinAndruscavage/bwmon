from .agent_based_api.v1 import *

def discover_ping_public_dns(section):
  yield Service()

def check_ping_public_dns(section):
  for line in section:
    if line[5].startswith(“0%”):
      yield Result(state=State.OK, summary=“Ping public dns ok”)
      return
    yield Result(state=State.CRIT, summary=“Ping public dns NOT ok”)

register.check_plugin(
  name=“ping_public_dns”,
  service_name=“Ping public dns (1.1.1.1)”,
  discovery_function=discover_ping_public_dns,
  check_function=check_ping_public_dns,
)
