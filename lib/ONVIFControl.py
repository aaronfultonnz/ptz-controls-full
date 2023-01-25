from onvif import ONVIFCamera


class ONVIFControl:

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

    def stop(self):
        self.ptz.Stop({'ProfileToken': self.profile_token})

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

    def preset_list(self):
        request = {'ProfileToken': self.profile_token}
        return self.ptz.GetPresets(request)

    def preset_goto(self, preset_id):
        request = {'ProfileToken': self.profile_token,
                   'PresetToken': preset_id,
                   }
        self.ptz.GotoPreset(request)

    def preset_add(self, name, preset_token):
        request = {'ProfileToken': self.profile_token,
                   'PresetName': name,
                   'PresetToken': preset_token,
                   }
        self.ptz.SetPreset(request)


if __name__ == '__main__':
    camera = ONVIFControl(host='192.168.1.176', port=80, username='admin', password='')
    camera.setup()
    camera.move(0, 1)
