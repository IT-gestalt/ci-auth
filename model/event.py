from dataclasses import dataclass, field


def empty_dict():
    return dict()


@dataclass
class Event:
    source: str
    destination: str
    operation: str
    parameters: dict = field(default_factory=empty_dict)

    def __eq__(self, other):
        if self.source == other.source and \
                self.destination == other.destination and \
                self.operation == other.operation:
            return True
        return False

    def get_source(self):
        return self.source
