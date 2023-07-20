import asyncio
import struct
from bleak import BleakScanner, BleakClient

settings_uuid = '53dc9a7a-bc19-4280-b76b-002d0e23b078'
read_uuid = '047d3559-8bee-423a-b229-4417fa603b90'

async def connect_to_pokit():
    devices = await BleakScanner.discover()
    pokit_device = None
    for device in devices:
        if device.name == "Pokit":
            pokit_device = device
            print("Found Pokit!")
            print(pokit_device)

    if pokit_device is not None:
        async with BleakClient(pokit_device) as client:
            # Set the measurement settings (replace the arguments with appropriate values)
            mode = 1  # for DC voltage
            range = 0  # 0V to 300mV
            update_interval = 1000  # 1000ms (1 second) update interval
            await set_measurement_settings(client, mode, range, update_interval)

            # Read and display voltage data continuously
            async for voltage in read_voltage(client):
                print("Voltage: {} V".format(voltage))
    else:
        print("Pokit device not found. Please make sure it is in range and advertising.")

async def set_measurement_settings(client, mode, range, update_interval):
    settings_data = bytearray([mode, range, update_interval & 0xFF, (update_interval >> 8) & 0xFF, (update_interval >> 16) & 0xFF, (update_interval >> 24) & 0xFF])
    await client.write_gatt_char(settings_uuid, settings_data)

async def read_voltage(client):
    while True:
        data = await client.read_gatt_char(read_uuid)
        voltage = struct.unpack('<f', data[1:5])[0]
        yield voltage
        # Add a delay to control the update interval
        await asyncio.sleep(1)  # Adjust the delay time as needed

asyncio.run(connect_to_pokit())
