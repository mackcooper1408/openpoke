# OpenPoke Fitness Coaching Extension

This document describes the fitness coaching capabilities added to OpenPoke, transforming it into a comprehensive personal AI assistant with specialized focus on health optimization through Whoop and Hevy integrations.

## Overview

OpenPoke has been extended with fitness coaching capabilities that allow the AI agent to:

- Monitor recovery, sleep, and strain data from Whoop
- Track workout history and progress through Hevy
- Design adaptive workout routines based on physiological data
- Provide personalized training recommendations
- Automatically check in on fitness goals using scheduled triggers

## New Features

### Whoop Integration

- **Recovery Tracking**: Monitor daily recovery scores to assess training readiness
- **Sleep Analysis**: Review sleep quality, duration, stages, and disturbances
- **Strain Monitoring**: Track cardiovascular load and exertion levels
- **Workout Activity**: View workout data tracked by Whoop sensors
- **Physiological Cycles**: Access complete cycle data combining recovery, strain, and sleep

### Hevy Integration

- **Workout History**: View past workouts with exercises, sets, reps, and weights
- **Routine Management**: Create and manage workout templates
- **Progress Tracking**: Monitor improvements over time
- **Workout Logging**: Record completed training sessions

### AI Fitness Coach Behavior

The execution agent now acts as a fitness coach that:

- Checks recovery data before recommending workouts
- Adapts training intensity based on physiological state
- Creates personalized workout routines in Hevy
- Sets up automated check-ins using triggers
- Provides data-driven fitness advice
- Celebrates achievements and provides motivation

## Setup Instructions

### 1. Environment Variables

Add the following to your `.env` file:

```bash
# Whoop OAuth Configuration
WHOOP_CLIENT_ID=your_whoop_client_id
WHOOP_CLIENT_SECRET=your_whoop_client_secret
WHOOP_REDIRECT_URI=http://localhost:3000/api/whoop/callback

# Hevy API Configuration (optional - can be set via UI)
HEVY_API_KEY=your_hevy_api_key
```

### 2. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### 3. Register Whoop OAuth Application

1. Go to [Whoop Developer Portal](https://developer.whoop.com/)
2. Create a new OAuth application
3. Set redirect URI to `http://localhost:3000/api/whoop/callback` (Next.js callback handler)
4. Copy the Client ID and Client Secret to your `.env` file
5. Request scopes: `read:recovery`, `read:sleep`, `read:workout`, `read:cycles`, `read:body_measurement`

### 4. Get Hevy API Key

1. Open the Hevy mobile app
2. Go to Settings → Developer
3. Generate an API key
4. Either add it to `.env` or enter it through the Settings UI

### 5. Start the Application

```bash
# Backend
cd server
python server.py

# Frontend (in another terminal)
cd web
npm install
npm run dev
```

### 6. Connect Services

1. Open the OpenPoke web interface
2. Click Settings (gear icon)
3. Under "Integrations":
   - Click "Connect Whoop" → Complete OAuth flow in popup
   - Enter your Hevy API key → Click "Connect Hevy"
4. Both services should show as "Connected"

## Usage Examples

### Morning Check-in

"Check my recovery and suggest today's workout"

The agent will:

1. Fetch your latest Whoop recovery score
2. Review sleep quality from last night
3. Check recent strain levels
4. Suggest an appropriate workout based on recovery state
5. Create a workout routine in Hevy if needed

### Weekly Progress Review

"Review my workout progress this week"

The agent will:

1. Fetch workout history from Hevy
2. Compare with previous weeks
3. Analyze recovery patterns from Whoop
4. Provide insights on training consistency and progress
5. Suggest adjustments to training plan

### Automated Daily Check-ins

"Set up a daily morning fitness check-in at 7 AM"

The agent will:

1. Ask for your preferences (frequency, focus areas)
2. Create a recurring trigger for daily check-ins
3. Each morning at 7 AM, automatically:
   - Review your recovery data
   - Assess readiness for training
   - Send recommendations via the chat interface

### Adaptive Workout Planning

"Create a 4-week progressive strength training program"

The agent will:

1. Review your current fitness level from Hevy history
2. Check typical recovery patterns from Whoop
3. Design a periodized program with progressive overload
4. Create routines in Hevy for each workout
5. Monitor execution and adapt based on recovery

## Architecture

### Backend Structure

```
server/
├── config.py                          # Added Whoop/Hevy environment variables
├── requirements.txt                   # Added requests library
├── agents/
│   └── execution_agent/
│       ├── system_prompt.md          # Updated with fitness coach persona
│       └── tools/
│           ├── whoop.py              # Whoop tool schemas and implementations
│           ├── hevy.py               # Hevy tool schemas and implementations
│           └── registry.py           # Registered new tools
├── services/
│   ├── whoop/
│   │   ├── __init__.py
│   │   └── client.py                 # OAuth flow, token storage, API calls
│   └── hevy/
│       ├── __init__.py
│       └── client.py                 # API key auth, workout/routine management
└── routes/
    ├── __init__.py                    # Registered new routers
    ├── whoop.py                       # OAuth endpoints
    └── hevy.py                        # API key management endpoints
```

### Frontend Structure

```
web/
└── components/
    └── SettingsModal.tsx              # Added Whoop/Hevy connection UI
```

### Token Storage

**Whoop**: OAuth tokens stored in `~/.openpoke/whoop_token.json`

- Automatic token refresh when expired
- Includes access token, refresh token, and expiry timestamp

**Hevy**: API key stored in `~/.openpoke/hevy_api_key.json`

- Validated on save
- Can also be set via environment variable

## API Endpoints

### Whoop Routes

- `GET /api/v1/whoop/connect` - Initiates OAuth flow
- `GET /api/v1/whoop/callback` - OAuth callback handler
- `GET /api/v1/whoop/status` - Check connection status
- `POST /api/v1/whoop/disconnect` - Disconnect and clear token

### Hevy Routes

- `POST /api/v1/hevy/connect` - Save and validate API key
- `GET /api/v1/hevy/status` - Check connection status
- `POST /api/v1/hevy/disconnect` - Clear API key

## Agent Tools

### Whoop Tools

- `whoop_get_recovery` - Fetch recovery scores
- `whoop_get_sleep` - Get sleep analysis
- `whoop_get_strain` - Review strain data
- `whoop_get_workouts` - View Whoop-tracked workouts
- `whoop_get_cycles` - Get complete physiological cycles

### Hevy Tools

- `hevy_get_workouts` - Fetch workout history
- `hevy_get_workout_details` - Get specific workout details
- `hevy_get_routines` - List all routines
- `hevy_get_routine_details` - Get specific routine structure
- `hevy_create_routine` - Design new workout plans
- `hevy_log_workout` - Record completed workouts

## Troubleshooting

### Whoop Connection Issues

- Ensure redirect URI matches exactly (including http/https)
- Check that all required scopes are granted
- Verify token hasn't expired (auto-refresh should handle this)
- Check `~/.openpoke/whoop_token.json` for token status

### Hevy Connection Issues

- Verify API key is valid in Hevy app settings
- Check that API key hasn't been revoked
- Ensure `~/.openpoke/hevy_api_key.json` has correct permissions

### Agent Not Using Fitness Tools

- Verify tools are registered in `tools/registry.py`
- Check system prompt includes fitness coaching instructions
- Ensure services are connected (check Settings UI)
- Review server logs for tool execution errors

## Future Enhancements

Potential areas for expansion:

1. **Additional Integrations**

   - Strava for running/cycling
   - MyFitnessPal for nutrition tracking
   - Apple Health / Google Fit for general health data

2. **Advanced Analytics**

   - Trend analysis and prediction
   - Overtraining detection
   - Performance optimization recommendations

3. **Social Features**

   - Workout sharing
   - Training partner matching
   - Group challenges

4. **Personalized Programming**
   - Machine learning for adaptive training plans
   - Injury prevention algorithms
   - Recovery optimization

## Contributing

When extending the fitness coaching capabilities:

1. Follow the existing pattern for tool creation
2. Add comprehensive tool schemas with clear descriptions
3. Update the system prompt with new capabilities
4. Add UI controls in SettingsModal for new integrations
5. Document all environment variables and setup steps

## License

Same as OpenPoke base project.
