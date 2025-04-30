from ulauncher.api import Extension


class DemoExtension(Extension):
    def on_input(self, input_text: str, trigger_id: str):
        for i in range(5):
            yield Result(
                name='Item %s' % i,
                description='Item description %s' % i
            )

if __name__ == '__main__':
    DemoExtension().run()