from time import sleep
from onvif import ONVIFCamera


class CameraControl:

    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.ptz = None
        self.imaging = None
        self.XMAX = 1
        self.XMIN = -1
        self.YMAX = 1
        self.YMIN = -1
        self.ZMAX = 1
        self.ZMIN = -1

    def setup(self):
        mycam = ONVIFCamera(self.host, self.port, self.username, self.password)
        media = mycam.create_media_service()
        self.ptz = mycam.create_ptz_service()
        self.imaging = mycam.create_imaging_service()
        media_profile = media.GetProfiles()[0]
        request = self.ptz.create_type('GetConfigurationOptions')
        request.ConfigurationToken = media_profile.PTZConfiguration.token
        self.video_token = media_profile.VideoSourceConfiguration.SourceToken
        ptz_configuration_options = self.ptz.GetConfigurationOptions(request)

        self.profile_token = media_profile.token
        self.XMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Max
        self.XMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].XRange.Min
        self.YMAX = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Max
        self.YMIN = ptz_configuration_options.Spaces.ContinuousPanTiltVelocitySpace[0].YRange.Min
        self.ZMIN = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Min
        self.ZMAX = ptz_configuration_options.Spaces.ContinuousZoomVelocitySpace[0].XRange.Max

    def move(self, x_speed, y_speed):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'PanTilt': {'x': x_speed, 'y': y_speed}},
                   }

        self.ptz.ContinuousMove(request)

    def zoom(self, speed):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'Zoom': {'x': speed}},
                   }
        self.ptz.ContinuousMove(request)

    def focus(self, speed):
        request = {'VideoSourceToken': self.video_token,
                   'Focus': {'Continuous': {'Speed': speed}},
                   }
        self.imaging.Move(request)

    def auto_focus(self):
        request = {'VideoSourceToken': self.video_token,
                   'ImagingSettings': {'Focus': {'AutoFocusMode': 'AUTO'}},
                   }
        self.imaging.SetImagingSettings(request)

    def manual_focus(self):
        request = {'VideoSourceToken': self.video_token,
                   'ImagingSettings': {'Focus': {'AutoFocusMode': 'MANUAL'}},
                   }
        self.imaging.SetImagingSettings(request)

    def stop(self):
        self.ptz.Stop({'ProfileToken': self.profile_token})

    def move_up(self, timeout=1):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'PanTilt': {'x': 0, 'y': self.YMAX}},
                   }

        self.ptz.ContinuousMove(request)
        sleep(timeout)
        self.stop()

    def move_down(self, timeout=1):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'PanTilt': {'x': 0, 'y': self.YMIN}},
                   }
        self.ptz.ContinuousMove(request)
        sleep(timeout)
        self.stop()

    def move_right(self, timeout=1):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'PanTilt': {'x': self.XMAX, 'y': 0}},
                   }
        self.ptz.ContinuousMove(request)
        sleep(timeout)
        self.stop()

    def move_left(self, timeout=1):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'PanTilt': {'x': self.XMIN, 'y': 0}},
                   }
        self.ptz.ContinuousMove(request)
        sleep(timeout)
        self.stop()

    def zoom_in(self, timeout=1):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'Zoom': {'x': self.ZMAX}},
                   }
        self.ptz.ContinuousMove(request)
        sleep(timeout)
        self.stop()

    def zoom_out(self, timeout=1):
        request = {'ProfileToken': self.profile_token,
                   'Velocity': {'Zoom': {'x': self.ZMIN}},
                   }
        self.ptz.ContinuousMove(request)
        sleep(timeout)
        self.stop()


if __name__ == '__main__':
    camera = CameraControl(host='192.168.1.176', port=80, username='admin', password='')
    camera.setup()
    camera.move(0.5, 0.1)
    print("Moving right")
    camera.move_right(5)
    print("Moving left")
    camera.move_left(5)
    print("Moving down")
    camera.move_down(5)
    print("Moving up")
    camera.move_up(5)
    print("Zoming in")
    camera.zoom_in(5)
    print("Zoming out")
    camera.zoom_out(5)
