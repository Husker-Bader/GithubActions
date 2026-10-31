import asyncio, edge_tts
from pathlib import Path
async def main():
    text="Welcome to signals and systems. Today we'll work through the problem carefully, one step at a time."
    await edge_tts.Communicate(text,voice="en-US-AvaNeural",rate="-12%").save("edge_test.mp3")
    assert Path("edge_test.mp3").stat().st_size > 1000
    print("OK",Path("edge_test.mp3").stat().st_size,flush=True)
asyncio.run(main())
