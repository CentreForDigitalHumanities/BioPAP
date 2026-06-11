












import re

a = "<class 'biopap.modules.set_channel_type_and_montage.SetChannelTypeAndMontage'>"

pattern = re.compile(r"^\<class \'biopap\.modules\.([a-z]+)\'\>$")

for name, obj in globals().items():
    if pattern.fullmatch(str(obj)):
        print(name, dir(obj), obj.__name__, str(obj))
