from pydantic import BaseModel


class SampleModel(BaseModel):
    id: int
    name = 'John Doe'


def main():
    external_data = {
        'id': '123',
        'name': 'John Doe'
    }
    model = SampleModel(**external_data)
    print("hello")
    print(model.id, model.name)


if __name__ == "__main__":
    main()
