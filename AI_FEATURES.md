# 🤖 AI-Powered Features in Goalin

Goalin now includes powerful AI features using Google's Gemini API to provide intelligent app categorization and productivity insights.

## Features

### 1. 🎯 Automatic App Categorization
- **Smart Detection**: Automatically detects all installed applications on your Linux system
- **AI Classification**: Uses Gemini AI to intelligently categorize apps into meaningful categories
- **Categories Include**:
  - Development (IDEs, code editors, terminals)
  - Browser (web browsers)
  - Communication (chat, email, video conferencing)
  - Media (video/audio players, editors)
  - Office (document editors, PDF readers)
  - Gaming (games and gaming platforms)
  - Productivity (task managers, note-taking)
  - Design (graphic design, 3D modeling)
  - System (file managers, settings)
  - Education (learning platforms, educational software)
  - Other (miscellaneous)

### 2. 📊 AI-Powered Productivity Analysis
- **Smart Scoring**: Calculates productivity score based on multiple factors:
  - Time spent in productive categories
  - Balance between different types of work
  - Consistency of work patterns
  - Deep focus sessions
- **Personalized Insights**: Get AI-generated insights about your work habits
- **Actionable Recommendations**: Receive specific suggestions to improve productivity

### 3. 🔒 Privacy-First Design
- **Your API Key**: Use your own Google Gemini API key
- **Local Processing**: App categorization data stored locally
- **No Data Sharing**: Your activity data never leaves your machine

## Setup

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key (starts with `AIza...`)

**Note**: The free tier includes:
- 60 requests per minute
- 1,500 requests per day
- Perfect for personal use!

### Initial Setup Wizard

When you first launch Goalin, you'll see the setup wizard:

1. **Welcome Screen**: Overview of AI features
2. **AI Configuration**: Enter your Gemini API key
3. **App Categorization**: AI automatically categorizes all your installed apps
4. **Complete**: Start using Goalin with AI features!

You can also run the setup wizard manually:
```bash
goalin-setup
```

### Skip AI Features

If you prefer to use Goalin without AI features:
- Click "Skip (Use Basic Mode)" during setup
- The app will use predefined keyword-based categorization
- You can enable AI features later in settings

## Usage

### App Categorization

Once configured, Goalin will:
- Automatically categorize new apps you use
- Store categories locally for instant access
- Update categories when you recategorize apps

### Productivity Reports

AI-enhanced reports include:
- **Productivity Score**: AI-calculated 0-100 score
- **Productivity Level**: High (80-100), Medium (50-79), Low (0-49)
- **AI Insights**: 3-5 specific observations about your work patterns
- **AI Recommendations**: 3-5 actionable suggestions for improvement

Example AI insights:
- "You have strong focus periods in the morning hours"
- "Browser usage suggests research-heavy work today"
- "Multiple short sessions - consider blocking time for deep work"

Example AI recommendations:
- "Consider scheduling your most demanding tasks during peak hours (9-11 AM)"
- "Reduce context switching by batching similar tasks together"
- "Take breaks between focus sessions to maintain productivity"

## Technical Details

### Files and Directories

- **AI Config**: `~/.config/goalin/ai_config.json`
  - Stores your encrypted API key
  
- **App Categories**: `~/.local/share/goalin/app_categories.json`
  - Cached app categorizations
  - Category definitions
  
- **Setup Marker**: `~/.config/goalin/.setup_complete`
  - Indicates setup has been completed

### API Usage

Typical usage per day:
- **Initial Setup**: 10-50 requests (depends on installed apps)
- **Daily Usage**: 1-5 requests (new apps + daily report)
- **Well within free tier limits**

### Fallback Behavior

If AI features are unavailable:
- Uses keyword-based categorization
- Basic productivity metrics
- No AI insights or recommendations
- Full app functionality maintained

## Reconfiguration

To reconfigure AI settings:

1. Delete setup marker:
   ```bash
   rm ~/.config/goalin/.setup_complete
   ```

2. Restart Goalin:
   ```bash
   goalin-gui
   ```

Or update API key directly:
```bash
# Edit the config file
nano ~/.config/goalin/ai_config.json
```

## Troubleshooting

### "Invalid API Key" Error
- Verify your API key is correct
- Check you have internet connection
- Ensure API key has proper permissions at Google AI Studio

### Slow Categorization
- Normal for large app collections (100+ apps)
- Categorization happens only once
- Subsequent launches are instant

### AI Analysis Not Showing
- Check your API key is configured
- Verify internet connectivity
- Look for errors in logs: `~/.local/share/goalin/logs/`

## Privacy & Security

### What Gets Sent to Google?
- **App Names Only**: During categorization
- **Activity Summary**: For productivity analysis (no specific websites/documents)
- **No Personal Data**: Window titles, file names, or sensitive info never sent

### What Stays Local?
- All activity tracking data
- Detailed usage logs
- Window titles and application details
- Your API key (encrypted)

## Benefits of AI Features

✅ **Accurate Categorization**: Better than keyword matching
✅ **Personalized Insights**: Tailored to your actual work patterns
✅ **Actionable Advice**: Specific recommendations you can implement
✅ **Continuous Learning**: Adapts as you use more applications
✅ **Time Saving**: No manual app categorization needed

## Future Enhancements

Planned AI features:
- Goal suggestions based on your work patterns
- Automatic time blocking recommendations
- Focus time optimization
- Weekly trend analysis with predictions
- Custom category creation

---

**Note**: AI features are optional. Goalin works perfectly fine without them using traditional keyword-based categorization!
