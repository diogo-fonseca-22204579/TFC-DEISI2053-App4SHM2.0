import 'package:animated_splash_screen/animated_splash_screen.dart';
import 'package:app4shm/pages/about_page.dart';
import 'package:app4shm/pages/damage_detection_page.dart';
import 'package:app4shm/pages/login_page.dart';
import 'package:app4shm/pages/power_spectrum_page.dart';
import 'package:app4shm/pages/time_series_page.dart';
import 'package:app4shm/providers/app_provider.dart';
import 'package:app4shm/theme.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:app4shm/pages/structures_page.dart';
import 'package:app4shm/pages/welcome_page.dart';
import 'package:provider/provider.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:page_transition/page_transition.dart';
import 'package:app4shm/pages/cable_force_page.dart';

import 'models/user.dart';

Future main() async {
  const bool isProduction = kReleaseMode;
  await dotenv.load(fileName: isProduction ? 'assets/env/.env-prod' : 'assets/env/.env-dev');
  SharedPreferences prefs = await SharedPreferences.getInstance();

  Brightness brightness = SchedulerBinding.instance.platformDispatcher.platformBrightness;
  bool darkModeOn = brightness == Brightness.dark;

  WidgetsFlutterBinding.ensureInitialized();

  if (kReleaseMode) {
    await SentryFlutter.init((options) {
      options.dsn = 'https://c68cf4b46d19c47de26cfb25f9947962@o4506772785332224.ingest.us.sentry.io/4507000997937152';
    }, appRunner: () async => runApp(await buildChangeNotifierProvider(darkModeOn, prefs)));
  } else {
    runApp(await buildChangeNotifierProvider(darkModeOn, prefs));
  }
}

Future<ChangeNotifierProvider<AppProvider>> buildChangeNotifierProvider(
    bool darkModeOn, SharedPreferences prefs) async {
  return ChangeNotifierProvider(
      create: (context) => AppProvider(),
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        // phone in dark mode ? darkTheme : lightTheme
        theme: darkModeOn ? await darkTheme() : await lightTheme(),
        home: Builder(
          builder: (context) {
            if (prefs.getString('userid') != null) {
              Provider.of<AppProvider>(context, listen: false).setUser(User(prefs.getString('userid')!));
            }

            return AnimatedSplashScreen(
              splash: 'assets/splash.png',
              nextScreen: prefs.getString('token') == null ? const LoginPage() : const StructuresPage(),
              pageTransitionType: PageTransitionType.rightToLeftWithFade,
              backgroundColor: const Color(0xFF01DEA0),
              splashIconSize: double.infinity,
            );
          },
        ),
        routes: {
          '/login': (context) => const LoginPage(),
          '/structures': (context) => const StructuresPage(),
          '/welcome': (context) => const WelcomePage(),
          '/timeseries': (context) => const TimeSeriesPage(),
          '/powerSpec': (context) => const PowerSpectrumPage(),
          '/result': (context) => const DamageDetectionPage(),
          '/about': (context) => const AboutPage(),
          '/cableforce': (context) => const CableForcePage(),
        },
      ));
}
