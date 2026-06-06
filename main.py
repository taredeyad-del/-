const { Client, GatewayIntentBits } = require('discord.js');

const client = new Client({ 
    intents: [
        GatewayIntentBits.Guilds, 
        GatewayIntentBits.GuildMessages, 
        GatewayIntentBits.MessageContent
    ] 
});

client.on('messageCreate', async message => {
    if (message.author.bot) return;

    // خريطة للأوامر والإيموجيات
    const commands = {
        '!شكوة': '🔴',
        '!طلب': '🔵',
        '!تماستلامطلب': '🟢',
        '!تمارسالطلب': '🟡'
    };

    const emoji = commands[message.content];

    // إذا كان الأمر موجوداً في القائمة
    if (emoji) {
        const channel = message.channel;
        let currentName = channel.name;

        // 1. إزالة أي إيموجي قديم من القائمة (🔴, 🔵, 🟢, 🟡)
        let cleanedName = currentName.replace(/🔴|🔵|🟢|🟡/g, '').replace(/-+/g, '-').replace(/-$/, '');

        // 2. دمج الاسم الجديد مع الإيموجي
        let newName = `${cleanedName}-${emoji}`;

        // 3. منع تكرار الإيموجي إذا كان موجوداً بالفعل
        newName = newName.replace(/-🔴/g, '🔴').replace(/-🔵/g, '🔵').replace(/-🟢/g, '🟢').replace(/-🟡/g, '🟡');

        try {
            await channel.setName(newName);
            message.reply(`تم تحديث حالة الروم إلى ${emoji}`);
        } catch (error) {
            console.error('Error changing channel name:', error);
            message.reply('حدث خطأ: تأكد من أن البوت لديه صلاحية "إدارة القنوات" (Manage Channels).');
        }
    }
});

client.login('YOUR_BOT_TOKEN_HERE');
