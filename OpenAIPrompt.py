from dotenv import load_dotenv
from openai import OpenAI
import os
import time

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
assistant_id = "asst_sHTR6T6rCTbD7V7wW6sOVsjb"

client = OpenAI(api_key=openai_key)
def load_transcript(transcriptfile):
    with open(transcriptfile, "r") as f:
        transcript = f.read()
        return transcript

def JupJuiceContext(transcriptfile):
    prompt = """Summarize the latest **Jup&Juice** podcast in a **fun and engaging Twitter Thread**! Include the **funniest moments**, **key discussions**, and any **insights or alpha dropped** by the hosts-**Wake and Sax**-or guests. Make sure to capture the **casual vibe**, the humor, and the playful back-and-forth. Add **emojis** and inject some excitement into it! Write the thread from the perspective of an **outside observer** (avoid phrases like \"We talked about...\"). Keep the tone lively, like you're catching up with a friend who missed out. Don’t forget to make it engaging and interactive! Some info: Jup&Juice's Twitter account is @JUPANDJUICE, this is where all the podcasts get streamed, and later uploaded. Include in the first Message that this was made possibly by Jupiter Horizon AI. Example: --- 🧵 [1] 🚀 Missed the latest Jup&Juice podcast? No worries, I got you! Let’s dive into the highlights from hosts Wake, Sax, and their guest Nom from the Bonk community! Buckle up for the funniest moments and key takeaways from this epic convo! 🎙️🍹 Powered by Jupiter Horizon AI 🤖 👇🧵 🧵 [2] Webcam Chaos & Scruffy Complaints 🎥 Wake and Sax joked about their old blurry webcams. Sax even had to shave because his wife had some complaints! 😂 They’re looking sharper these days, but blurry cams hide the blemishes, right? 🤷‍♂️ 🧵 [3] From 8 Viewers to 230+ 🎉 They reminisced about humble beginnings when they'd wonder if only 8 friends would show up. Now, they hit 100 viewers almost immediately! Talk about leveling up! 🚀 The community is growing strong, all thanks to your support! 💖 🧵 [4] Bonk Saving Elephants & Dogs 🐘🐕 Nom dropped some alpha—Bonk helped rescue an elephant named Bonnie in Africa! 🌍 And they're also saving doggos worldwide! 🐾 Bonk isn’t just memes and tokens; they’re making real-world impact! 🙌 Talk about PPP vibes! 🧵 [5] Nom: The Bonk Janitor 🧹 Nom humbly referred to himself as the “janitor” of Bonk, cleaning up and doing all the behind-the-scenes work that makes everything run smoothly. But hey, plumbers and janitors make the world go round, right? 🚿 🧵 [6] Pooper Scooper? Best Product Name Ever! 💩🐕 Speaking of funny names, Bonk’s product “Pooper Scooper” was a fan favorite! It swaps all your dust (those tiny leftover tokens) into Bonk tokens. I mean, who wouldn’t love a product that turns trash into treasure? 🤣 🧵 [7] Wake vs. Sax: Gamer Showdown 🎮 The banter was real when the conversation turned competitive! Wake and Sax argued over who’s the better gamer—chess, pool, Warzone, you name it. 🎯 Who do you think would win in a Warzone showdown? 🗳️ Place your bets! 🧵 [8] Nom’s Fitness Hack 🏃‍♂️ On a lighter note, Nom shared how he tries to stay healthy by walking while catching up on DMs. Treadmill chats, anyone? 💬🏋️‍♂️ Gotta get those steps in while building Bonk, am I right? 🧵 [9] Breakpoint Bonk Bash 🎈 At Breakpoint, Bonk made waves with a giant inflatable Shiba Inu dog! 🐕🎈 Their IRL events are unmissable. Bonk knows how to throw a party! 🌟 🧵 [10] The Bigger Picture: Bonk’s Charity Work 🌟 Nom emphasized that Bonk’s goal isn’t just pumping meme coins but creating real-world change. 🌍 From saving elephants to helping dog rescues. Bonk is making a difference, and they're not slowing down! 💪 🧵 [11] PPP Vibes Strong 🚀 The episode wrapped up with a reminder: PPP (People Pumping People) is the ethos of both the Bonk and Jupiter communities. 💖Whether through charity, community growth, or just some good old laughs, the future of DeFi is all about lifting each other up! 🚀 🧵 [12] 🎉 Missed the episode? Catch the full convo on Jup & Juice’s Account: @JUPANDJUICE ! 🍹Stay tuned for more alpha, banter, and laughs from the Jupiverse 🌌. Brought to you by the Jupiter Horizon AI! 🤖 Try it out yourself here ✨: https://chatgpt.com/g/g-RdJ5Sbwwu-jupiter-horizon Be sure to follow @Jup_juice for more laid-back fun and real alpha! 🍹 --- **Jupiter Context:** \"Jupiter is a comprehensive and dynamic decentralized finance (DeFi) platform built on the Solana blockchain, offering a wide range of financial products and services. Initially known for its role as a top-performing aggregator for token swaps, it has since evolved into a robust ecosystem supporting perpetual trading, governance, and liquidity provision. The Jupiverse, as it’s often referred to, encompasses several core components: 1. Trading and Financial Products: Jupiter allows users to trade tokens through swaps, limit orders, and dollar-cost averaging strategies. Its Perpetual Exchange and liquidity pools enhance users’ ability to participate in high-throughput, low-cost trading on Solana. 2. Jupiter Token ($JUP): $JUP is the platform’s native governance token. It plays a crucial role in governance, allowing holders to participate in DAO votes and decisions affecting platform direction. Users can stake $JUP to earn rewards and contribute to decentralized governance. 3. Launchpad: The LFG Launchpad on Jupiter is designed to support the launch of new projects within the Solana ecosystem, with the community voting on which projects to support. 4. DAO and Governance: The Jupiter DAO empowers users to vote on key governance decisions, including new project launches, strategic changes, and tokenomics proposals. Active stakers of $JUP earn rewards, incentivizing long-term participation and alignment with the platform’s growth. 5. Innovative Tools: Jupiter also provides a wide array of trading tools, including advanced routing algorithms, a bridge comparator for cross-chain transfers, and the JupSOL product, which integrates a liquid staking solution with Jupiter’s validator to offer yield enhancements to the community. Through a combination of these features, Jupiter has established itself as a central hub in the Solana DeFi ecosystem, continually evolving to meet the needs of its users while supporting the broader development of decentralized finance ￼ ￼.\" **Base the entire Recap Post ONLY on the following Transcript.** **Transcript:**\n
    """

    thread = client.beta.threads.create()

    transcript = load_transcript(transcriptfile)

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"{prompt}{transcript}"
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    while run.status != 'completed':
        run = client.beta.threads.runs.poll(run_id=run.id, thread_id=thread.id)
        print(run.status)
        if run.status == "failed":
            print(run.last_error)
        time.sleep(5)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(messages)


if __name__ == "__main__":
    JupJuiceContext("OutputFiles/JUP & JUICE 23 | Uprock & Gurk_transcription.txt")